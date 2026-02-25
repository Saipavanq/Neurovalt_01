from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    database_url: str = "sqlite:///./neurovault.db"
    embedding_model: str = "all-MiniLM-L6-v2"
    faiss_index_path: str = "./faiss_indexes"
    faiss_nlist: int = 100
    faiss_nprobe: int = 10

    # Cognitive score weights
    cognitive_weight_semantic: float = 0.6
    cognitive_weight_recency: float = 0.2
    cognitive_weight_access: float = 0.2

    # Recency decay
    recency_decay_lambda: float = 0.1

    # Lifecycle thresholds
    tier_active_threshold: float = 0.75
    tier_contextual_threshold: float = 0.50
    tier_archived_threshold: float = 0.25

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    class Config:
        env_file = ".env"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def faiss_index_dir(self) -> Path:
        p = Path(self.faiss_index_path)
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()
