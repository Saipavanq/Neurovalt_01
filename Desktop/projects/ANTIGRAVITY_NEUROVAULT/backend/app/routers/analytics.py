from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.document import Document
from app.schemas.document import AnalyticsResponse, TierStats, DocumentResponse
from app.services.cognition import cognition_engine, TIER_COLORS

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

TIER_ORDER = ["Active", "Contextual", "Archived", "Dormant"]


@router.get("/", response_model=AnalyticsResponse)
def get_analytics(
    user_id: str = Query(default="default_user"),
    db: Session = Depends(get_db),
):
    docs = db.query(Document).filter(Document.user_id == user_id).all()
    total = len(docs)
    avg_score = sum(d.cognitive_score for d in docs) / total if total else 0.0

    # Tier distribution
    tier_counts: dict[str, list[float]] = {t: [] for t in TIER_ORDER}
    for d in docs:
        tier_counts[d.tier].append(d.cognitive_score)

    tier_stats = [
        TierStats(
            tier=tier,
            count=len(scores),
            avg_score=sum(scores) / len(scores) if scores else 0.0,
            color=TIER_COLORS.get(tier, "#888"),
        )
        for tier in TIER_ORDER
        for scores in [tier_counts[tier]]
    ]

    # Top documents by cognitive score
    top_docs = sorted(docs, key=lambda d: d.cognitive_score, reverse=True)[:10]

    return AnalyticsResponse(
        total_documents=total,
        tier_distribution=tier_stats,
        avg_cognitive_score=round(avg_score, 4),
        top_documents=[_to_resp(d) for d in top_docs],
    )


@router.get("/lifecycle")
def lifecycle_data(
    user_id: str = Query(default="default_user"),
    db: Session = Depends(get_db),
):
    """Score histogram data for D3.js visualization."""
    docs = db.query(Document).filter(Document.user_id == user_id).all()
    nodes = [
        {
            "id": d.id,
            "filename": d.filename,
            "score": round(d.cognitive_score, 4),
            "tier": d.tier,
            "access_count": d.access_count,
            "file_type": d.file_type,
            "color": TIER_COLORS.get(d.tier, "#888"),
            "created_at": d.created_at.isoformat(),
            "last_accessed": d.last_accessed.isoformat(),
        }
        for d in docs
    ]

    # Histogram buckets (10 buckets from 0 to 1)
    buckets = [0] * 10
    for d in docs:
        idx = min(9, int(d.cognitive_score * 10))
        buckets[idx] += 1

    histogram = [
        {"range": f"{i/10:.1f}–{(i+1)/10:.1f}", "count": buckets[i]}
        for i in range(10)
    ]

    return {
        "nodes": nodes,
        "histogram": histogram,
        "tier_thresholds": {
            "active": 0.75,
            "contextual": 0.50,
            "archived": 0.25,
        },
    }


@router.get("/tiers")
def tier_summary(
    user_id: str = Query(default="default_user"),
    db: Session = Depends(get_db),
):
    docs = db.query(Document).filter(Document.user_id == user_id).all()
    result = {}
    for tier in TIER_ORDER:
        tier_docs = [d for d in docs if d.tier == tier]
        result[tier] = {
            "count": len(tier_docs),
            "avg_score": (
                round(sum(d.cognitive_score for d in tier_docs) / len(tier_docs), 4)
                if tier_docs else 0.0
            ),
            "color": TIER_COLORS.get(tier, "#888"),
            "description": cognition_engine.tier_description(tier),
        }
    return result


# ──────────────────────────────────────────
def _to_resp(doc: Document) -> DocumentResponse:
    return DocumentResponse(
        id=doc.id,
        user_id=doc.user_id,
        filename=doc.filename,
        file_type=doc.file_type,
        tier=doc.tier,
        cognitive_score=doc.cognitive_score,
        semantic_score=doc.semantic_score,
        access_count=doc.access_count,
        last_accessed=doc.last_accessed,
        created_at=doc.created_at,
        chunk_count=doc.chunk_count,
        file_size=doc.file_size,
        description=doc.description,
        project_tags=doc.get_project_tags(),
    )
