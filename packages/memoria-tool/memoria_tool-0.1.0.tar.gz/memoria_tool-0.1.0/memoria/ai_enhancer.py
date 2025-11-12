import warnings
import nltk
from .core import generate_insight  # Reuse cloud logic

# Download required NLTK resources quietly at import time
nltk.download('vader_lexicon', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('maxent_ne_chunker', quiet=True)
nltk.download('words', quiet=True)

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import word_tokenize, pos_tag, ne_chunk


class AIEnhancer:
    """Advanced AI features: sentiment, entity extraction,
    question answering, topic modeling, and recommendations.
    Supports local (NLTK, sklearn, transformers) and cloud APIs.
    """

    def __init__(self, vault):
        self.vault = vault
        self.sia = SentimentIntensityAnalyzer()

    def sentiment_analysis(self, text: str, provider: str = 'local', api_key: str = None, model: str = None) -> dict:
        """Analyze sentiment. Local (VADER) or cloud provider."""
        if provider != 'local':
            warnings.warn("Cloud provider used for sentiment analysis—data sent externally.")
        if provider == 'local':
            return self.sia.polarity_scores(text)

        prompt = f"Analyze sentiment of: {text}. Return as JSON: {{positive: float, negative: float, neutral: float}}"
        return eval(generate_insight([], provider, api_key, model, prompt=prompt))

    def entity_extraction(self, text: str, provider: str = 'local', api_key: str = None, model: str = None) -> list[str]:
        """Extract named entities (persons, places). Local (NLTK) or cloud provider."""
        if provider != 'local':
            warnings.warn("Cloud provider used for entity extraction—data sent externally.")
        if provider == 'local':
            tokens = word_tokenize(text)
            tagged = pos_tag(tokens)
            entities = ne_chunk(tagged)
            return [chunk[0] for chunk in entities if hasattr(chunk, 'label')]
        
        prompt = f"Extract entities from: {text}. Return as list."
        return eval(generate_insight([], provider, api_key, model, prompt=prompt))

    def question_answering(self, question: str, context: str, provider: str = 'local', api_key: str = None, model: str = None) -> str:
        """Answer questions based on context. Local (transformers) or cloud provider."""
        if provider != 'local':
            warnings.warn("Cloud provider used for question answering—data sent externally.")
        if provider == 'local':
            from transformers import pipeline
            qa_pipeline = pipeline('question-answering', model='distilbert-base-cased-distilled-squad')
            return qa_pipeline(question=question, context=context)['answer']

        prompt = f"Answer the question based on this context: {context}\nQuestion: {question}"
        return generate_insight([], provider, api_key, model, prompt=prompt)

    def topic_modeling(self, texts: list[str], provider: str = 'local', api_key: str = None, model: str = None) -> dict:
        """Cluster texts into topics. Local (sklearn) or cloud provider."""
        if provider != 'local':
            warnings.warn("Cloud provider used for topic modeling—data sent externally.")
        if provider == 'local':
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.cluster import KMeans
            vectorizer = TfidfVectorizer(max_features=100)
            X = vectorizer.fit_transform(texts)
            kmeans = KMeans(n_clusters=3)
            kmeans.fit(X)
            # Map cluster labels to example texts
            clusters = {}
            for label, text in zip(kmeans.labels_, texts):
                clusters.setdefault(label, []).append(text)
            return clusters

        prompt = f"Cluster these texts into topics: {texts}. Return as JSON dict."
        return eval(generate_insight([], provider, api_key, model, prompt=prompt))

    def context_aware_recommendation(self, memories: list[dict], provider: str = 'local', api_key: str = None, model: str = None) -> str:
        """Suggest next actions based on memories. Local simple or cloud advanced."""
        if provider != 'local':
            warnings.warn("Cloud provider used for recommendations—data sent externally.")
        context = "\n".join([f"{m['content']} ({m['source']})" for m in memories])
        if provider == 'local':
            return f"Based on recent memories, consider reviewing: {context[:100]}..."
        prompt = f"Based on these memories, suggest next actions: {context}"
        return generate_insight([], provider, api_key, model, prompt=prompt)
