import os
import numpy as np
import faiss
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DIMENSION = 384


class FaissService:
    """
    Manages per-user FAISS IVF indexes for cosine similarity search.
    Vectors are L2-normalized so inner product == cosine similarity.
    """

    _instance: Optional["FaissService"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._indexes: dict[str, faiss.IndexFlatIP] = {}
            cls._instance._id_maps: dict[str, dict[int, str]] = {}  # faiss_id -> doc_id
            cls._instance._counters: dict[str, int] = {}
            cls._instance._index_dir: Optional[Path] = None
        return cls._instance

    def init(self, index_dir: Path):
        self._index_dir = index_dir
        index_dir.mkdir(parents=True, exist_ok=True)

    def _get_index(self, user_id: str) -> faiss.IndexFlatIP:
        """Get or create an inner-product (cosine) flat index for a user."""
        if user_id not in self._indexes:
            # Try loading from disk first
            idx_path = self._index_path(user_id)
            if idx_path.exists():
                logger.info(f"Loading FAISS index for user {user_id}")
                self._indexes[user_id] = faiss.read_index(str(idx_path))
            else:
                logger.info(f"Creating new FAISS index for user {user_id}")
                self._indexes[user_id] = faiss.IndexFlatIP(DIMENSION)
            self._id_maps.setdefault(user_id, {})
            self._counters.setdefault(user_id, 0)
        return self._indexes[user_id]

    def _index_path(self, user_id: str) -> Path:
        safe = user_id.replace("/", "_").replace("\\", "_")
        return self._index_dir / f"index_{safe}.bin"

    def add_vectors(
        self, user_id: str, doc_id: str, vectors: np.ndarray
    ) -> list[int]:
        """Add multiple chunk vectors for a document. Returns list of FAISS IDs."""
        index = self._get_index(user_id)
        start = self._counters.get(user_id, 0)
        n = vectors.shape[0]
        faiss_ids = list(range(start, start + n))
        self._counters[user_id] = start + n

        for fid in faiss_ids:
            self._id_maps[user_id][fid] = doc_id

        index.add(vectors)
        self._save_index(user_id)
        return faiss_ids

    def search(
        self, user_id: str, query_vec: np.ndarray, k: int = 10
    ) -> list[dict]:
        """
        Search the index. Returns list of {doc_id, score} dicts.
        Deduplicates by doc_id, keeping best score.
        """
        index = self._get_index(user_id)
        if index.ntotal == 0:
            return []

        k = min(k * 5, index.ntotal)  # oversample to account for duplicates
        query = query_vec.reshape(1, -1).astype(np.float32)
        distances, ids = index.search(query, k)

        id_map = self._id_maps.get(user_id, {})
        seen: dict[str, float] = {}
        for dist, fid in zip(distances[0], ids[0]):
            if fid == -1:
                continue
            doc_id = id_map.get(int(fid))
            if doc_id and (doc_id not in seen or dist > seen[doc_id]):
                seen[doc_id] = float(dist)

        results = [{"doc_id": d, "semantic_score": s} for d, s in seen.items()]
        results.sort(key=lambda x: x["semantic_score"], reverse=True)
        return results

    def remove_document(self, user_id: str, faiss_ids: list[int]):
        """Mark FAISS IDs as removed from the id_map (flat index cannot remove)."""
        id_map = self._id_maps.get(user_id, {})
        for fid in faiss_ids:
            id_map.pop(fid, None)

    def _save_index(self, user_id: str):
        if self._index_dir:
            faiss.write_index(self._indexes[user_id], str(self._index_path(user_id)))

    def get_stats(self, user_id: str) -> dict:
        index = self._get_index(user_id)
        return {
            "total_vectors": index.ntotal,
            "dimension": DIMENSION,
            "user_id": user_id,
        }


faiss_service = FaissService()
