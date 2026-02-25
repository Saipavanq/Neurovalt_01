# NeuroVault 🧠

**AI-Powered Cognitive Storage Intelligence System**

> Transforms passive file storage into a cognitive intelligence layer using vector embeddings, FAISS similarity indexing, cognitive scoring, memory lifecycle management, and explainable AI retrieval.

---

## Architecture

```
File Upload → OCR/Parser → Chunking → Embedding (384-dim) → FAISS Index → Metadata Store
User Query → Embed → FAISS Search → Cognitive Re-rank → Explainable Results
```

### Cognitive Scoring Formula
```
Score = 0.6 × Semantic Similarity
      + 0.2 × Recency (e^(-λt))
      + 0.2 × Access Frequency (log(1+count))
```

### Memory Lifecycle Tiers
| Score | Tier | Storage |
|-------|------|---------|
| ≥ 0.75 | 🟢 Active | Hot |
| 0.50–0.74 | 🔵 Contextual | Warm |
| 0.25–0.49 | 🟠 Archived | Cold |
| < 0.25 | ⚫ Dormant | Deep Archive |

---

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env

# Start server
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 2. Frontend Setup

```bash
cd frontend
npm run dev
```

App: http://localhost:5173

---

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, SQLAlchemy |
| Database | SQLite (local) / PostgreSQL |
| AI/ML | sentence-transformers, FAISS-CPU |
| Parser | PyPDF2, python-docx, pytesseract |
| Frontend | React, Vite, TailwindCSS, D3.js |

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/documents/upload` | Upload & index document |
| `GET` | `/api/documents/` | List documents |
| `DELETE` | `/api/documents/{id}` | Delete document |
| `POST` | `/api/search/` | Semantic search |
| `GET` | `/api/analytics/` | Full analytics |
| `GET` | `/api/analytics/lifecycle` | D3 lifecycle data |
| `GET` | `/api/analytics/tiers` | Tier breakdown |
| `GET` | `/health` | Health check |

---

## Supported File Types

- **PDF** — text extraction via PyPDF2
- **DOCX** — via python-docx
- **TXT / MD / CSV** — direct UTF-8
- **PNG / JPG / TIFF** — OCR via pytesseract
