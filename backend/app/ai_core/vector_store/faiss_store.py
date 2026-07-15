"""
Thin wrapper around a FAISS flat inner-product index (cosine similarity,
since embeddings are L2-normalized at generation time). One index per
entity type ("resumes", "jobs"), persisted to disk under ml_core/artifacts/
so it survives process restarts without recomputing every embedding.

This is intentionally simple (IndexFlatIP, exact search) — appropriate for
a dataset of thousands to low-millions of resumes/jobs. If the corpus grows
much larger, swap IndexFlatIP for IndexIVFFlat behind this same interface.
"""
from __future__ import annotations

import json
import os
import threading

import numpy as np

_ARTIFACT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "ml_core", "artifacts")


class FaissStore:
    def __init__(self, namespace: str, dimension: int):
        self.namespace = namespace
        self.dimension = dimension
        self._lock = threading.Lock()
        os.makedirs(_ARTIFACT_DIR, exist_ok=True)
        self._index_path = os.path.join(_ARTIFACT_DIR, f"faiss_{namespace}.index")
        self._ids_path = os.path.join(_ARTIFACT_DIR, f"faiss_{namespace}_ids.json")
        self._id_map: list[str] = []  # FAISS row -> our entity id (string)
        self._index = self._load_or_create()

    def _load_or_create(self):
        import faiss  # lazy import — heavy dependency

        if os.path.exists(self._index_path) and os.path.exists(self._ids_path):
            index = faiss.read_index(self._index_path)
            with open(self._ids_path) as f:
                self._id_map = json.load(f)
            return index
        return faiss.IndexFlatIP(self.dimension)

    def _persist(self) -> None:
        import faiss

        faiss.write_index(self._index, self._index_path)
        with open(self._ids_path, "w") as f:
            json.dump(self._id_map, f)

    def add(self, entity_id: str, vector: list[float]) -> int:
        """Adds/updates a vector, returns its FAISS row index."""
        with self._lock:
            arr = np.array([vector], dtype="float32")
            self._index.add(arr)
            self._id_map.append(entity_id)
            self._persist()
            return len(self._id_map) - 1

    def search(self, vector: list[float], top_k: int = 10) -> list[tuple[str, float]]:
        if self._index.ntotal == 0:
            return []
        arr = np.array([vector], dtype="float32")
        scores, indices = self._index.search(arr, min(top_k, self._index.ntotal))
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            results.append((self._id_map[idx], float(score)))
        return results

    def rebuild(self, entity_ids: list[str], vectors: list[list[float]]) -> None:
        """Full rebuild from scratch — used by the admin-triggered reindex job."""
        import faiss

        with self._lock:
            self._index = faiss.IndexFlatIP(self.dimension)
            if vectors:
                self._index.add(np.array(vectors, dtype="float32"))
            self._id_map = list(entity_ids)
            self._persist()


_stores: dict[str, FaissStore] = {}


def get_faiss_store(namespace: str) -> FaissStore:
    from app.core.config import get_settings

    if namespace not in _stores:
        settings = get_settings()
        _stores[namespace] = FaissStore(namespace, settings.EMBEDDING_DIMENSION)
    return _stores[namespace]
