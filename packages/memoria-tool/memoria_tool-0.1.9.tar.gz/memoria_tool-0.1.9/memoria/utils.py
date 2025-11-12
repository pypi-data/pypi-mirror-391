import numpy as np
from sentence_transformers import SentenceTransformer
from cryptography.fernet import Fernet, InvalidToken

# Load lightweight embedding model (runs locally)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embedding(text: str) -> np.ndarray:
    """Generate vector embedding for text."""
    return embedding_model.encode(text)

def encrypt_data(key: bytes, data: str) -> bytes:
    """Encrypt string data using Fernet (AES)."""
    fernet = Fernet(key)
    return fernet.encrypt(data.encode())

def decrypt_data(key: bytes, encrypted_data: bytes) -> str:
    """Decrypt data; raises error on failure."""
    try:
        fernet = Fernet(key)
        return fernet.decrypt(encrypted_data).decode()
    except InvalidToken:
        raise ValueError("Invalid encryption key or corrupted data.")