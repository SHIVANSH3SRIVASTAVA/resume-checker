from sentence_transformers import SentenceTransformer
import numpy as np

_model = SentenceTransformer("all-MiniLM-L6-v2")

def embed(text: str) -> list:
    vec = _model.encode([text], normalize_embeddings=True)[0]
    return vec.tolist()

def cosine(a: list, b: list) -> float:
    a = np.array(a); b = np.array(b)
    return float(np.clip(np.dot(a, b), -1.0, 1.0))
