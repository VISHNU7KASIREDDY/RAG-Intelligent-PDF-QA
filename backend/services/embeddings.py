"""
Embeddings service using Google Gemini text-embedding-004.
"""
import numpy as np
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

MODEL = "models/gemini-embedding-001"
EMBEDDING_DIM = 3072


def embed_texts(texts: list[str]) -> np.ndarray:
    """
    Generate embeddings for a batch of texts using Gemini.

    Args:
        texts: List of text strings to embed.

    Returns:
        numpy array of shape (len(texts), EMBEDDING_DIM), L2-normalized.
    """
    all_embeddings = []
    batch_size = 100  # Gemini batch limit

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        result = genai.embed_content(
            model=MODEL,
            content=batch,
            task_type="RETRIEVAL_DOCUMENT",
        )
        all_embeddings.extend(result["embedding"])

    arr = np.array(all_embeddings, dtype=np.float32)
    # L2-normalize for cosine similarity via inner product
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms[norms == 0] = 1
    arr = arr / norms
    return arr


def embed_query(query: str) -> np.ndarray:
    """
    Generate embedding for a single query using Gemini.

    Returns:
        numpy array of shape (1, EMBEDDING_DIM), L2-normalized.
    """
    result = genai.embed_content(
        model=MODEL,
        content=query,
        task_type="RETRIEVAL_QUERY",
    )
    arr = np.array([result["embedding"]], dtype=np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms[norms == 0] = 1
    arr = arr / norms
    return arr
