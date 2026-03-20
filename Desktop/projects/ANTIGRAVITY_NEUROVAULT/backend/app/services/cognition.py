import math
from datetime import datetime
from typing import Literal
from app.config import settings

TierName = Literal["Active", "Contextual", "Archived", "Dormant"]

TIER_COLORS = {
    "Active": "#00ff88",
    "Contextual": "#00d4ff",
    "Archived": "#ff9500",
    "Dormant": "#666688",
}

TIER_DESCRIPTIONS = {
    "Active": "Hot Tier — frequently accessed, highly relevant",
    "Contextual": "Warm Tier — moderately relevant, recent context",
    "Archived": "Cold Tier — low activity, infrequent access",
    "Dormant": "Deep Archive — rarely accessed, low relevance",
}


class CognitionEngine:
    """
    Computes multi-factor cognitive relevance scores and classifies
    documents into lifecycle tiers.

    Formula:
        score = 0.6×semantic + 0.2×recency + 0.2×access
    """

    def __init__(self):
        self.w_semantic = settings.cognitive_weight_semantic
        self.w_recency = settings.cognitive_weight_recency
        self.w_access = settings.cognitive_weight_access
        self.lambda_decay = settings.recency_decay_lambda

    def recency_score(self, last_accessed: datetime) -> float:
        """Exponential decay: e^(-λ·days_since_access)."""
        now = datetime.utcnow()
        delta_days = max(0.0, (now - last_accessed).total_seconds() / 86400.0)
        return math.exp(-self.lambda_decay * delta_days)

    def access_score(self, access_count: int) -> float:
        """Normalized log score: log(1+count) / log(1+100)."""
        return math.log(1 + access_count) / math.log(1 + 100)

    def compute_score(
        self,
        semantic_similarity: float,
        last_accessed: datetime,
        access_count: int,
    ) -> float:
        """Compute composite cognitive relevance score in [0, 1]."""
        r = self.recency_score(last_accessed)
        a = self.access_score(access_count)
        score = (
            self.w_semantic * semantic_similarity
            + self.w_recency * r
            + self.w_access * a
        )
        return min(1.0, max(0.0, score))

    def compute_storage_score(self, last_accessed: datetime, access_count: int) -> float:
        """Score without query context (for background reclassification)."""
        return self.compute_score(0.5, last_accessed, access_count)

    def classify_tier(self, score: float) -> TierName:
        if score >= settings.tier_active_threshold:
            return "Active"
        elif score >= settings.tier_contextual_threshold:
            return "Contextual"
        elif score >= settings.tier_archived_threshold:
            return "Archived"
        else:
            return "Dormant"

    def tier_color(self, tier: str) -> str:
        return TIER_COLORS.get(tier, "#888888")

    def tier_description(self, tier: str) -> str:
        return TIER_DESCRIPTIONS.get(tier, "")

    def score_components(
        self, semantic: float, last_accessed: datetime, access_count: int
    ) -> dict:
        r = self.recency_score(last_accessed)
        a = self.access_score(access_count)
        total = self.compute_score(semantic, last_accessed, access_count)
        return {
            "total": round(total, 4),
            "semantic": round(semantic, 4),
            "recency": round(r, 4),
            "access": round(a, 4),
            "semantic_weighted": round(self.w_semantic * semantic, 4),
            "recency_weighted": round(self.w_recency * r, 4),
            "access_weighted": round(self.w_access * a, 4),
        }


cognition_engine = CognitionEngine()
