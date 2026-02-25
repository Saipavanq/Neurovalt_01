from datetime import datetime
from app.services.cognition import cognition_engine


def _days_since(dt: datetime) -> float:
    return max(0.0, (datetime.utcnow() - dt).total_seconds() / 86400.0)


def _recency_label(days: float) -> str:
    if days < 1:
        return "Accessed today"
    elif days < 3:
        return "Recent activity detected"
    elif days < 7:
        return "Accessed this week"
    elif days < 30:
        return "Accessed this month"
    else:
        return f"Last accessed {int(days)} days ago"


def _access_label(count: int, days_since_first: float) -> str:
    if days_since_first < 1:
        days_since_first = 1
    per_week = count / max(1, days_since_first / 7)
    if per_week >= 5:
        return f"{count}× accessed — very frequent"
    elif per_week >= 2:
        return f"{count}× accessed this period — frequent"
    elif count >= 3:
        return f"{count}× accessed"
    elif count == 1:
        return "Accessed once"
    else:
        return "Rarely accessed"


class ExplainerService:
    """Builds rich, human-readable explanations for every retrieval result."""

    def build(
        self,
        doc_id: str,
        filename: str,
        semantic_similarity: float,
        last_accessed: datetime,
        access_count: int,
        created_at: datetime,
        tier: str,
    ) -> dict:
        components = cognition_engine.score_components(
            semantic_similarity, last_accessed, access_count
        )
        days = _days_since(last_accessed)
        days_since_created = _days_since(created_at)

        semantic_pct = int(round(semantic_similarity * 100))
        recency_lbl = _recency_label(days)
        access_lbl = _access_label(access_count, days_since_created)

        tier_color = cognition_engine.tier_color(tier)
        tier_desc = cognition_engine.tier_description(tier)

        explanation = (
            f"Matched {semantic_pct}% semantically to your query. "
            f"{recency_lbl}. {access_lbl}. "
            f"Classified as {tier} ({tier_desc})."
        )

        return {
            "final_score": components["total"],
            "semantic_similarity": components["semantic"],
            "semantic_percentage": semantic_pct,
            "semantic_weighted": components["semantic_weighted"],
            "recency_score": components["recency"],
            "recency_weighted": components["recency_weighted"],
            "recency_label": recency_lbl,
            "access_score": components["access"],
            "access_weighted": components["access_weighted"],
            "access_label": access_lbl,
            "tier": tier,
            "tier_color": tier_color,
            "tier_description": tier_desc,
            "explanation": explanation,
        }


explainer_service = ExplainerService()
