# memoria/core.py

import datetime
import warnings
import time

import faiss
import numpy as np
from sqlalchemy import create_engine, Column, Integer, String, BLOB, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from transformers import pipeline  # Local LLM

# Import optional cloud providers with safe exception handling
try:
    import google.generativeai as genai  # Gemini
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import openai  # OpenAI/ChatGPT
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic  # Claude
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from .utils import generate_embedding, encrypt_data, decrypt_data, get_embedding_dimension


Base = declarative_base()


class Memory(Base):
    __tablename__ = 'memories'

    id = Column(Integer, primary_key=True)
    encrypted_content = Column(BLOB, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    source = Column(String, nullable=False)
    embedding = Column(BLOB, nullable=False)  # Stored as bytes


class MemoryVault:
    """Encrypted local database for memories."""

    def __init__(self, db_path: str = 'memoria.db', key: bytes = None):
        if not key:
            raise ValueError("Encryption key must be provided.")
        self.key = key
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self._build_faiss_index()  # Initialize or load FAISS index

    def _build_faiss_index(self):
        """Build or rebuild FAISS index from database memories."""
        session = self.Session()
        try:
            memories = session.query(Memory).all()
            
            if memories:
                # Reconstruct embeddings from bytes
                embeddings_list = []
                for m in memories:
                    embedding = np.frombuffer(m.embedding, dtype=np.float32)
                    embeddings_list.append(embedding)
                
                embeddings = np.array(embeddings_list)
                dim = embeddings.shape[1]
                self.faiss_index = faiss.IndexFlatL2(dim)
                self.faiss_index.add(embeddings)
                self.memory_ids = [m.id for m in memories]
            else:
                # No memories yet - create empty index with correct dimension
                dim = get_embedding_dimension()  # Dynamically get dimension from model
                self.faiss_index = faiss.IndexFlatL2(dim)
                self.memory_ids = []
                
        finally:
            session.close()

    def add_memory(self, content: str, timestamp: datetime.datetime, source: str = "user") -> Memory:
        """Add a memory with encrypted content and embedding."""
        # Generate and validate embedding
        embedding = generate_embedding(content).astype(np.float32)  # Ensure float32
        if embedding.ndim != 1:
            embedding = embedding.flatten()  # Ensure 1-D
        
        # Encrypt content
        encrypted_content = encrypt_data(self.key, content)
        embedding_bytes = embedding.tobytes()
        
        # Store in database
        memory = Memory(
            encrypted_content=encrypted_content,
            embedding=embedding_bytes,
            timestamp=timestamp,
            source=source
        )
        
        session = self.Session()
        try:
            session.add(memory)
            session.commit()
            session.refresh(memory)
            
            # Add to FAISS index with proper shape
            if self.faiss_index is not None:
                # Reshape to (1, dim) for FAISS
                embedding_2d = np.expand_dims(embedding, axis=0)
                self.faiss_index.add(embedding_2d)
                self.memory_ids.append(memory.id)
                
            return memory
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_memories(self, ids: list[int]) -> list[dict]:
        """Fetch and decrypt memories by IDs."""
        session = self.Session()
        try:
            memories = session.query(Memory).filter(Memory.id.in_(ids)).all()
            results = []
            for m in memories:
                decrypted = decrypt_data(self.key, m.encrypted_content)
                results.append({
                    'id': m.id,
                    'content': decrypted,
                    'timestamp': m.timestamp,
                    'source': m.source
                })
            return results
        finally:
            session.close()


class SemanticSearcher:
    """Semantic search over embeddings."""

    def __init__(self, vault: MemoryVault):
        self.vault = vault

    def query(self, natural_query: str, top_k: int = 10) -> list[dict]:
        """Search via semantic similarity."""
        query_embedding = generate_embedding(natural_query).reshape(1, -1)
        distances, indices = self.vault.faiss_index.search(query_embedding, top_k)
        matching_ids = [self.vault.memory_ids[idx] for idx in indices[0] if idx < len(self.vault.memory_ids)]
        return self.vault.get_memories(matching_ids)


class TimelineManager:
    """Chronological playback and insights."""

    def __init__(self, vault: MemoryVault):
        self.vault = vault

    def get_playback(self, start_time: datetime.datetime, end_time: datetime.datetime) -> list[dict]:
        """Get events in a specific time range."""
        session = self.vault.Session()
        try:
            memories = (session.query(Memory)
                                .filter(Memory.timestamp.between(start_time, end_time))
                                .order_by(Memory.timestamp)
                                .all())
            results = []
            for m in memories:
                decrypted = decrypt_data(self.vault.key, m.encrypted_content)
                results.append({
                    'content': decrypted,
                    'timestamp': m.timestamp,
                    'source': m.source
                })
            return results
        finally:
            session.close()

    def generate_insight(
        self,
        events: list[dict],
        provider: str = 'local',
        api_key: str = None,
        model: str = None,
        prompt: str = None
    ) -> str:
        """
        Generate insight summary. Supports local or cloud providers.

        Parameters:
        - provider: 'local' (transformers), 'gemini', 'openai', 'anthropic', 'perplexity', 'grok'.
        - api_key: Required for cloud providers.
        - model: Optional model name (e.g., 'gemini-1.5-pro', 'gpt-4o', 'claude-3-5-sonnet-20240620').
        - prompt: Optional custom prompt (otherwise uses default summarization prompt).

        Warning:
        - Cloud providers send data externally — privacy risk.
        """
        if not events and prompt is None:
            return "No events in this range."

        if provider != 'local':
            warnings.warn("Using cloud provider sends data externally. Ensure compliance with privacy policies.")

        # Use custom prompt if provided, otherwise create default
        if prompt is None:
            event_text = "\n".join([f"{e['timestamp']}: {e['content']} ({e['source']})" for e in events])
            prompt = f"Summarize these events concisely: {event_text}"

        for attempt in range(3):  # Retry with exponential backoff for rate limits
            try:
                if provider == 'local':
                    summarizer = pipeline('summarization', model='t5-small')
                    return summarizer(prompt, max_length=100)[0]['summary_text']

                elif provider == 'gemini':
                    if not GEMINI_AVAILABLE:
                        raise ImportError("Google Generative AI library not installed. Install with 'pip install google-generativeai'")
                    if not api_key:
                        raise ValueError("API key required for Gemini.")
                    genai.configure(api_key=api_key)
                    model_instance = genai.GenerativeModel(model or 'gemini-1.5-pro')
                    response = model_instance.generate_content(prompt)
                    return response.text

                elif provider in ('openai', 'perplexity'):
                    if not OPENAI_AVAILABLE:
                        raise ImportError("OpenAI library not installed. Install with 'pip install openai'")
                    if not api_key:
                        raise ValueError("API key required.")
                    base_url = "https://api.perplexity.ai" if provider == 'perplexity' else None
                    client = openai.OpenAI(api_key=api_key, base_url=base_url)
                    response = client.chat.completions.create(
                        model=model or 'gpt-4o',
                        messages=[{"role": "user", "content": prompt}]
                    )
                    return response.choices[0].message.content

                elif provider == 'anthropic':
                    if not ANTHROPIC_AVAILABLE:
                        raise ImportError("Anthropic library not installed. Install with 'pip install anthropic'")
                    if not api_key:
                        raise ValueError("API key required for Anthropic.")
                    client = anthropic.Anthropic(api_key=api_key)
                    response = client.messages.create(
                        model=model or 'claude-3-5-sonnet-20240620',
                        max_tokens=100,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    return response.content[0].text

                elif provider == 'grok':
                    if not REQUESTS_AVAILABLE:
                        raise ImportError("Requests library not installed. Install with 'pip install requests'")
                    if not api_key:
                        raise ValueError("API key required for Grok.")
                    response = requests.post(
                        'https://api.x.ai/v1/chat/completions',  # Hypothetical endpoint
                        headers={'Authorization': f'Bearer {api_key}'},
                        json={'model': model or 'grok-3', 'messages': [{'role': 'user', 'content': prompt}]}
                    )
                    response.raise_for_status()
                    return response.json()['choices'][0]['message']['content']

                else:
                    raise ValueError(f"Unsupported provider: {provider}")

            except Exception as e:
                # Safe exception handling without referencing potentially unavailable modules
                error_msg = str(e)
                
                # Check for rate limit patterns in error message
                rate_limit_indicators = [
                    'rate limit', 'ratelimit', 'too many requests', 
                    'quota exceeded', '429', 'rate_limit'
                ]
                
                is_rate_limit = any(indicator in error_msg.lower() for indicator in rate_limit_indicators)
                
                if is_rate_limit and attempt < 2:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                
                # Re-raise with informative message
                if attempt == 2:
                    raise Exception(f"API error after {attempt + 1} attempts: {error_msg}")
                else:
                    raise