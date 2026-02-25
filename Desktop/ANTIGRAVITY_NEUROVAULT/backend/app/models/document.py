import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON
from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(100), index=True, nullable=False)
    filename = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    content_text = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0)

    # Cognitive state
    tier = Column(String(20), default="Contextual")  # Active, Contextual, Archived, Dormant
    cognitive_score = Column(Float, default=0.0)
    semantic_score = Column(Float, default=0.0)

    # Lifecycle signals
    access_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # FAISS references (list of int IDs stored as JSON)
    faiss_ids = Column(Text, default="[]")

    # File metadata
    file_size = Column(Integer, default=0)
    project_tags = Column(Text, default="[]")  # JSON list of tags
    description = Column(Text, nullable=True)

    def get_faiss_ids(self) -> list[int]:
        return json.loads(self.faiss_ids or "[]")

    def set_faiss_ids(self, ids: list[int]):
        self.faiss_ids = json.dumps(ids)

    def get_project_tags(self) -> list[str]:
        return json.loads(self.project_tags or "[]")

    def set_project_tags(self, tags: list[str]):
        self.project_tags = json.dumps(tags)
