import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Singleton wrapper around sentence-transformers all-MiniLM-L6-v2."""

    _instance: Optional["EmbeddingService"] = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self, model_name: str = "all-MiniLM-L6-v2"):
        if self._model is None:
            logger.info(f"Loading embedding model: {model_name}")
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(model_name)
            logger.info("Embedding model loaded successfully.")

    def encode(self, texts: list[str]) -> np.ndarray:
        """Encode texts to 384-dimensional float32 vectors."""
        if self._model is None:
            self.load()
        if not texts:
            return np.zeros((0, 384), dtype=np.float32)
        vecs = self._model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return vecs.astype(np.float32)

    def encode_single(self, text: str) -> np.ndarray:
        """Encode a single text, return shape (384,)."""
        return self.encode([text])[0]

    @property
    def dimension(self) -> int:
        return 384


embedding_service = EmbeddingService()
