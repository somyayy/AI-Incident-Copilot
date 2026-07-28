"""
FAISS-backed vector store for retrieving semantically similar past incidents.

The index is persisted to disk (VECTOR_DB_PATH) so it survives restarts.
Each stored vector is paired with incident metadata (id, title, summary text)
in a parallel docstore dict.
"""

import os
import pickle
from typing import Optional

import faiss
import numpy as np

from app.config import get_settings
from app.rag.embeddings import embed_documents, embed_text
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

_EMBEDDING_DIM = 1536  # dimensionality of text-embedding-3-small


class IncidentVectorStore:
    """Thin wrapper around a FAISS flat index plus a metadata docstore."""

    def __init__(self, index_path: str):
        self.index_path = index_path
        self.meta_path = f"{index_path}.meta.pkl"
        self.index: faiss.Index = faiss.IndexFlatL2(_EMBEDDING_DIM)
        self.docstore: list[dict] = []  # position i <-> vector row i
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "rb") as f:
                self.docstore = pickle.load(f)
            logger.info("Loaded FAISS index with %d vectors", self.index.ntotal)
        else:
            logger.info("No existing FAISS index found, starting fresh")

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.index_path) or ".", exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "wb") as f:
            pickle.dump(self.docstore, f)

    def add_incident(self, incident_id: str, title: str, text: str) -> None:
        vector = embed_text(text)
        arr = np.array([vector], dtype="float32")
        self.index.add(arr)
        self.docstore.append({"id": incident_id, "title": title, "text": text})
        self.save()

    def add_incidents_bulk(self, records: list[dict]) -> None:
        """records: [{id, title, text}, ...]"""
        vectors = embed_documents([r["text"] for r in records])
        arr = np.array(vectors, dtype="float32")
        self.index.add(arr)
        self.docstore.extend(records)
        self.save()

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        if self.index.ntotal == 0:
            return []
        query_vector = np.array([embed_text(query)], dtype="float32")
        distances, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            record = dict(self.docstore[idx])
            record["distance"] = float(dist)
            results.append(record)
        return results


_store: Optional[IncidentVectorStore] = None


def get_vector_store() -> IncidentVectorStore:
    global _store
    if _store is None:
        _store = IncidentVectorStore(settings.vector_db_path)
    return _store
