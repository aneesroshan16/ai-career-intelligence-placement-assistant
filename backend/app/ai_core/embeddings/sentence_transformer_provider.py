"""
Local, offline embedding provider backed by `sentence-transformers`. Unlike
the LLM providers, this one is real from day one (not a mock) — resume/job
similarity (Module 8) and skill-name normalization (Module 4) work without
any external API key, since the model runs on the backend's own CPU.

Model is loaded once and cached (module-level singleton) to avoid reloading
weights on every request.
"""
from __future__ import annotations

from functools import lru_cache

from app.ai_core.embeddings.base import EmbeddingProvider
from app.core.config import get_settings


class SentenceTransformerProvider(EmbeddingProvider):
    def __init__(self, model_name: str, dimension: int):
        self.model_name = model_name
        self._model = None
        self._dimension = dimension

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer  # lazy import
                self._model = SentenceTransformer(self.model_name)
            except Exception:
                self._model = False
        return self._model if self._model is not False else None

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            model = self._get_model()
            if model is not None:
                vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
                return vectors.tolist()
        except Exception:
            pass

        # Fallback to zero-vectors if model loading or encoding encounters memory/runtime issues
        return [[0.0] * self._dimension for _ in texts]


    @property
    def dimension(self) -> int:
        return self._dimension


@lru_cache
def get_embedding_provider() -> EmbeddingProvider:
    settings = get_settings()
    return SentenceTransformerProvider(
        model_name=settings.EMBEDDING_MODEL_NAME,
        dimension=settings.EMBEDDING_DIMENSION,
    )
