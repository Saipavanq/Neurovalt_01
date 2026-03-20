import time
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.document import Document
from app.schemas.search import SearchRequest, SearchResponse, SearchResult, ScoreBreakdown
from app.services.embedding_service import embedding_service
from app.services.faiss_service import faiss_service
from app.services.cognition import cognition_engine
from app.services.explainer import explainer_service
from app.services.parser_service import parser_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/search", tags=["search"])


@router.post("/", response_model=SearchResponse)
def semantic_search(req: SearchRequest, db: Session = Depends(get_db)):
    """
    Query Pipeline:
    User Query → Embed → FAISS Vector Search → Cognitive Re-rank → Explainable Results
    """
    t0 = time.perf_counter()

    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # 1. Embed the query
    query_vec = embedding_service.encode_single(req.query)

    # 2. FAISS vector similarity search
    raw_results = faiss_service.search(req.user_id, query_vec, k=req.k * 3)

    if not raw_results:
        return SearchResponse(
            query=req.query,
            total_results=0,
            results=[],
            query_time_ms=round((time.perf_counter() - t0) * 1000, 2),
        )

    # 3. Fetch documents and cognitive re-rank
    ranked = []
    for item in raw_results:
        doc = db.query(Document).filter(Document.id == item["doc_id"]).first()
        if not doc or doc.user_id != req.user_id:
            continue

        semantic_sim = float(item["semantic_score"])

        # Apply cognitive scoring on top of semantic
        cognitive_score = cognition_engine.compute_score(
            semantic_sim, doc.last_accessed, doc.access_count
        )
        tier = cognition_engine.classify_tier(cognitive_score)

        # Apply filters
        if req.tier_filter and tier != req.tier_filter:
            continue
        if cognitive_score < req.min_score:
            continue

        # Build explanation
        explanation = explainer_service.build(
            doc.id, doc.filename, semantic_sim,
            doc.last_accessed, doc.access_count, doc.created_at, tier
        )

        ranked.append({
            "doc": doc,
            "semantic": semantic_sim,
            "cognitive": cognitive_score,
            "tier": tier,
            "explanation": explanation,
        })

    # 4. Sort by cognitive score descending
    ranked.sort(key=lambda x: x["cognitive"], reverse=True)
    ranked = ranked[:req.k]

    # 5. Update document access states in DB
    for item in ranked:
        doc = item["doc"]
        doc.semantic_score = item["semantic"]
        doc.cognitive_score = item["cognitive"]
        doc.tier = item["tier"]

    db.commit()

    # 6. Build response
    results = []
    for rank, item in enumerate(ranked, start=1):
        doc = item["doc"]
        exp = item["explanation"]
        snippet = parser_service.get_preview(doc.content_text or "", 250)

        breakdown = ScoreBreakdown(
            semantic_similarity=exp["semantic_similarity"],
            semantic_percentage=exp["semantic_percentage"],
            recency_score=exp["recency_score"],
            recency_label=exp["recency_label"],
            access_score=exp["access_score"],
            access_label=exp["access_label"],
            tier=exp["tier"],
            final_score=exp["final_score"],
            explanation=exp["explanation"],
        )

        results.append(SearchResult(
            document_id=doc.id,
            filename=doc.filename,
            file_type=doc.file_type,
            tier=item["tier"],
            final_score=item["cognitive"],
            content_snippet=snippet,
            breakdown=breakdown,
            rank=rank,
        ))

    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)

    return SearchResponse(
        query=req.query,
        total_results=len(results),
        results=results,
        query_time_ms=elapsed_ms,
    )
