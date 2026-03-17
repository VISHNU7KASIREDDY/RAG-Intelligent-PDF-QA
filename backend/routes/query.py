"""
Query and summarize routes.
"""
from fastapi import APIRouter, HTTPException
from models.schemas import QueryRequest, QueryResponse
from services.rag_pipeline import query, summarize_documents

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Ask a question against uploaded PDF documents.
    Returns an answer with source references.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        result = query(
            question=request.question,
            chat_history=request.chat_history,
        )
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}",
        )


@router.post("/summarize", response_model=QueryResponse)
async def summarize():
    """
    Summarize all uploaded documents.
    """
    try:
        result = summarize_documents()
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating summary: {str(e)}",
        )
