import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.services.embedding_service import embedding_service
from app.services.faiss_service import faiss_service
from app.routers import documents, search, analytics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────
    logger.info("🚀 NeuroVault starting up...")

    # Initialize database tables
    init_db()
    logger.info("✅ Database initialized")

    # Pre-load embedding model (blocks until ready)
    embedding_service.load(settings.embedding_model)
    logger.info("✅ Embedding model loaded")

    # Initialize FAISS index directory
    faiss_service.init(settings.faiss_index_dir)
    logger.info("✅ FAISS service initialized")

    logger.info("🧠 NeuroVault is ready!")
    yield

    # ── Shutdown ─────────────────────────────────────────────────
    logger.info("NeuroVault shutting down...")


app = FastAPI(
    title="NeuroVault API",
    description="Cognitive Storage Intelligence System — semantic search, lifecycle scoring & explainable retrieval",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow the React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(documents.router)
app.include_router(search.router)
app.include_router(analytics.router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "NeuroVault",
        "version": "1.0.0",
        "embedding_model": settings.embedding_model,
    }


@app.get("/")
def root():
    return {
        "message": "Welcome to NeuroVault — Cognitive Storage Intelligence",
        "docs": "/docs",
        "health": "/health",
    }
