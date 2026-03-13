"""
FastAPI main application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from routes.upload import router as upload_router
from routes.query import router as query_router

app = FastAPI(
    title="PDF Question Answering System",
    description="RAG-based PDF QA using Claude and FAISS",
    version="1.0.0",
)

# CORS — allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(upload_router, tags=["Upload"])
app.include_router(query_router, tags=["Query"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "PDF QA System"}
