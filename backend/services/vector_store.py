"""
FAISS-based vector store with metadata support and persistence.
"""
import faiss
import numpy as np
import json
import os
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
INDEX_PATH = DATA_DIR / "faiss.index"
METADATA_PATH = DATA_DIR / "metadata.json"


class VectorStore:
    """FAISS vector store with metadata tracking."""
    def __init__(self):
        self.dimension = 3072  # Gemini embedding-001 dimension
        self.index: faiss.IndexFlatIP | None = None
        self.metadata: list[dict] = []
        self._load()

    def _load(self):
        """Load existing index and metadata from disk."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        if INDEX_PATH.exists() and METADATA_PATH.exists():
            self.index = faiss.read_index(str(INDEX_PATH))
            with open(METADATA_PATH, "r") as f:
                self.metadata = json.load(f)
        else:
            self.index = faiss.IndexFlatIP(self.dimension)
            self.metadata = []

    def add_documents(
        self,
        embeddings: np.ndarray,
        metadata_list: list[dict],
    ) -> None:
        """
        Add document embeddings and metadata to the store.

        Args:
            embeddings: numpy array of shape (n, dimension).
            metadata_list: List of metadata dicts (one per embedding).
        """
        if embeddings.shape[0] != len(metadata_list):
            raise ValueError("Embeddings and metadata count mismatch")

        self.index.add(embeddings)
        self.metadata.extend(metadata_list)
        self._save()

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
    ) -> list[dict]:
        """
        Search for most similar documents.

        Args:
            query_embedding: numpy array of shape (1, dimension).
            top_k: Number of results to return.

        Returns:
            List of dicts with keys: score, document_id, page_number, chunk_text
        """
        if self.index.ntotal == 0:
            return []

        # Clamp top_k to available vectors
        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query_embedding, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            meta = self.metadata[idx].copy()
            meta["score"] = float(score)
            results.append(meta)

        return results

    def get_document_chunks(self, document_id: str) -> list[dict]:
        """Get all chunks belonging to a specific document."""
        return [m for m in self.metadata if m.get("document_id") == document_id]

    def get_all_documents(self) -> list[str]:
        """Get unique document IDs in the store."""
        return list(set(m.get("document_id", "") for m in self.metadata))

    def _save(self):
        """Persist index and metadata to disk."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(INDEX_PATH))
        with open(METADATA_PATH, "w") as f:
            json.dump(self.metadata, f)

    def clear(self):
        """Clear all data."""
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = []
        self._save()


# Singleton instance
vector_store = VectorStore()
