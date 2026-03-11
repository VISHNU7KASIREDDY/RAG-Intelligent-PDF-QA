# PDF Q&A — Intelligent Document Assistant

A full-stack RAG (Retrieval-Augmented Generation) PDF Question Answering System built **without** LangChain or LlamaIndex.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + Vite |
| Backend | FastAPI (Python) |
| LLM | Claude (Anthropic) |
| Embeddings | OpenAI `text-embedding-3-small` |
| Vector DB | FAISS (local) |
| PDF Processing | PyMuPDF |

## Features

- **PDF Upload** — Drag & drop PDF upload with multi-document support
- **Question Answering** — Ask questions and get answers grounded in document content
- **Source Citations** — Every answer includes page numbers and text snippets
- **Chat Memory** — Follow-up questions with conversation context
- **Document Summarization** — One-click summary of all uploaded documents
- **Premium UI** — Dark theme with glassmorphism, animations, and responsive design

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- API keys:
  - `ANTHROPIC_API_KEY` (for Claude LLM)
  - `OPENAI_API_KEY` (for embeddings)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your API keys

# Start server
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

## API Endpoints

### `GET /health`

Health check.

```json
{ "status": "ok", "service": "PDF QA System" }
```

### `POST /upload`

Upload a PDF file.

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@document.pdf"
```

**Response:**
```json
{
  "document_id": "uuid",
  "filename": "document.pdf",
  "num_chunks": 42,
  "message": "Successfully processed 'document.pdf' into 42 chunks."
}
```

### `POST /query`

Ask a question.

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'
```

**Response:**
```json
{
  "answer": "The document discusses...",
  "sources": [
    { "page": 3, "text": "relevant snippet...", "filename": "document.pdf" }
  ]
}
```

### `POST /summarize`

Summarize all uploaded documents.

```bash
curl -X POST http://localhost:8000/summarize
```

## Architecture

```
User Question → Embed Query → FAISS Search (top-5) → Build Context → Claude LLM → Answer + Sources
```

### RAG Pipeline

1. **PDF Processing**: PyMuPDF extracts text per page with cleaning
2. **Chunking**: Sentence-aware splitting (600 tokens, 100 overlap)
3. **Embedding**: OpenAI `text-embedding-3-small` (1536 dimensions)
4. **Storage**: FAISS `IndexFlatIP` with L2-normalized vectors (cosine similarity)
5. **Retrieval**: Top-5 most relevant chunks via vector search
6. **Generation**: Claude answers strictly from retrieved context

## Project Structure

```
RAG/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── requirements.txt
│   ├── .env.example
│   ├── routes/
│   │   ├── upload.py         # POST /upload
│   │   └── query.py          # POST /query, /summarize
│   ├── services/
│   │   ├── pdf_loader.py     # PDF text extraction
│   │   ├── chunking.py       # Sentence-aware chunking
│   │   ├── embeddings.py     # OpenAI embeddings
│   │   ├── vector_store.py   # FAISS index management
│   │   └── rag_pipeline.py   # Orchestration
│   ├── models/
│   │   └── schemas.py        # Pydantic models
│   ├── utils/
│   └── data/                 # FAISS index persistence
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── api.js
│   │   ├── index.css
│   │   └── components/
│   │       ├── Upload.jsx
│   │       ├── Chat.jsx
│   │       ├── Message.jsx
│   │       └── Sources.jsx
└── README.md
```
