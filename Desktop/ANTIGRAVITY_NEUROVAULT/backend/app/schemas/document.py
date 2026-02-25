from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DocumentBase(BaseModel):
    filename: str
    file_type: str
    description: Optional[str] = None
    project_tags: list[str] = []


class DocumentCreate(DocumentBase):
    user_id: str


class DocumentResponse(BaseModel):
    id: str
    user_id: str
    filename: str
    file_type: str
    tier: str
    cognitive_score: float
    semantic_score: float
    access_count: int
    last_accessed: datetime
    created_at: datetime
    chunk_count: int
    file_size: int
    description: Optional[str] = None
    project_tags: list[str] = []

    class Config:
        from_attributes = True


class DocumentDetail(DocumentResponse):
    content_preview: Optional[str] = None
    explanation: Optional[dict] = None


class TierStats(BaseModel):
    tier: str
    count: int
    avg_score: float
    color: str


class AnalyticsResponse(BaseModel):
    total_documents: int
    tier_distribution: list[TierStats]
    avg_cognitive_score: float
    top_documents: list[DocumentResponse]
