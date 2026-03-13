from pydantic import BaseModel
from typing import Optional


class Source(BaseModel):
    page: int
    text: str


class QueryRequest(BaseModel):
    question: str
    chat_history: Optional[list[dict]] = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    num_chunks: int
    message: str
