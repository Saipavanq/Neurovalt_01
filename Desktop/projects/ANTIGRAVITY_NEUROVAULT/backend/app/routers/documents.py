import uuid
import logging
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentResponse, DocumentDetail
from app.services.embedding_service import embedding_service
from app.services.faiss_service import faiss_service
from app.services.parser_service import parser_service
from app.services.cognition import cognition_engine
from app.services.explainer import explainer_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/documents", tags=["documents"])

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
    "text/markdown": "md",
    "text/csv": "csv",
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/tiff": "tiff",
}


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Query(default="default_user"),
    description: str = Query(default=""),
    db: Session = Depends(get_db),
):
    """Upload a document: parse → chunk → embed → index → store."""
    content_type = file.content_type or "text/plain"
    file_type = ALLOWED_TYPES.get(content_type, content_type.split("/")[-1])

    file_bytes = await file.read()
    file_size = len(file_bytes)

    # Parse
    text = parser_service.extract_text(file_bytes, file_type)
    if not text.strip():
        text = f"[No text extracted from {file.filename}]"

    # Chunk
    chunks = parser_service.chunk_text(text)
    if not chunks:
        chunks = [text[:512]]

    # Embed
    vectors = embedding_service.encode(chunks)

    # Compute initial cognitive score (no query context)
    now = datetime.utcnow()
    initial_score = cognition_engine.compute_storage_score(now, 0)
    tier = cognition_engine.classify_tier(initial_score)

    # Store document
    doc_id = str(uuid.uuid4())
    doc = Document(
        id=doc_id,
        user_id=user_id,
        filename=file.filename,
        file_type=file_type,
        content_text=text,
        chunk_count=len(chunks),
        tier=tier,
        cognitive_score=initial_score,
        semantic_score=0.0,
        access_count=0,
        last_accessed=now,
        created_at=now,
        file_size=file_size,
        description=description,
    )
    db.add(doc)
    db.flush()  # get the id

    # Index in FAISS
    faiss_ids = faiss_service.add_vectors(user_id, doc_id, vectors)
    doc.set_faiss_ids(faiss_ids)
    db.commit()
    db.refresh(doc)

    logger.info(f"Uploaded: {file.filename} → {doc_id} ({len(chunks)} chunks, tier={tier})")
    return _to_response(doc)


@router.get("/", response_model=list[DocumentResponse])
def list_documents(
    user_id: str = Query(default="default_user"),
    tier: str = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(Document).filter(Document.user_id == user_id)
    if tier:
        q = q.filter(Document.tier == tier)
    docs = q.order_by(Document.cognitive_score.desc()).offset(skip).limit(limit).all()
    return [_to_response(d) for d in docs]


@router.get("/{doc_id}", response_model=DocumentDetail)
def get_document(doc_id: str, db: Session = Depends(get_db)):
    doc = _get_doc_or_404(doc_id, db)
    resp = _to_response(doc)
    detail = DocumentDetail(
        **resp.model_dump(),
        content_preview=parser_service.get_preview(doc.content_text or ""),
        explanation=explainer_service.build(
            doc.id,
            doc.filename,
            doc.semantic_score,
            doc.last_accessed,
            doc.access_count,
            doc.created_at,
            doc.tier,
        ),
    )
    return detail


@router.delete("/{doc_id}")
def delete_document(
    doc_id: str,
    user_id: str = Query(default="default_user"),
    db: Session = Depends(get_db),
):
    doc = _get_doc_or_404(doc_id, db)
    faiss_service.remove_document(user_id, doc.get_faiss_ids())
    db.delete(doc)
    db.commit()
    return {"status": "deleted", "doc_id": doc_id}


@router.post("/{doc_id}/access")
def record_access(
    doc_id: str,
    query_used: str = Query(default=""),
    relevance_score: float = Query(default=0.0),
    db: Session = Depends(get_db),
):
    doc = _get_doc_or_404(doc_id, db)
    doc.access_count += 1
    doc.last_accessed = datetime.utcnow()
    new_score = cognition_engine.compute_storage_score(doc.last_accessed, doc.access_count)
    doc.cognitive_score = new_score
    doc.tier = cognition_engine.classify_tier(new_score)
    db.commit()
    return {"status": "ok", "cognitive_score": new_score, "tier": doc.tier}


# ──────────────────────────────────────────
def _get_doc_or_404(doc_id: str, db: Session) -> Document:
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


def _to_response(doc: Document) -> DocumentResponse:
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
