from typing import Optional
from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    k: int = 5
    user_id: str
    min_score: float = 0.0
    tier_filter: Optional[str] = None  # e.g. "Active", "Contextual"


class ScoreBreakdown(BaseModel):
    semantic_similarity: float
    semantic_percentage: int
    recency_score: float
    recency_label: str
    access_score: float
    access_label: str
    tier: str
    final_score: float
    explanation: str


class SearchResult(BaseModel):
    document_id: str
    filename: str
    file_type: str
    tier: str
    final_score: float
    content_snippet: str
    breakdown: ScoreBreakdown
    rank: int


class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: list[SearchResult]
    query_time_ms: float
