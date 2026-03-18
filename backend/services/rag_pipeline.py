"""
RAG pipeline: orchestrates PDF processing and question answering.
Uses Google Gemini for both LLM responses and embeddings.
"""
import uuid
import os
from dotenv import load_dotenv
import google.generativeai as genai

from services.pdf_loader import extract_text_from_pdf
from services.chunking import chunk_pages
from services.embeddings import embed_texts, embed_query
from services.vector_store import vector_store

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

GEMINI_MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """You are an AI assistant that answers questions based ONLY on the provided context from PDF documents.

Rules:
1. Answer ONLY using the provided context. Do not use any prior knowledge.
2. If the answer is not found in the context, say: "Not found in document."
3. Be concise and accurate.
4. When possible, reference the page number(s) where you found the information.
5. If the context contains partial information, provide what you can and note the limitations."""

QA_PROMPT_TEMPLATE = """Context from documents:
{context}

Question: {question}

Provide a clear, accurate answer based ONLY on the above context."""

SUMMARY_PROMPT = """You are an AI assistant. Summarize the following document content clearly and concisely.
Cover the main topics, key points, and important details.

Document content:
{context}

Provide a comprehensive summary."""


def process_pdf(file_bytes: bytes, filename: str) -> dict:
    """
    Full pipeline: extract text → chunk → embed → store in vector DB.

    Args:
        file_bytes: Raw PDF bytes.
        filename: Original filename.

    Returns:
        Dict with document_id, filename, num_chunks.
    """
    document_id = str(uuid.uuid4())

    # 1. Extract text from PDF
    pages = extract_text_from_pdf(file_bytes)

    if not pages:
        raise ValueError("No text could be extracted from the PDF. The file may be empty or image-based.")

    # 2. Chunk the text
    chunks = chunk_pages(pages, document_id=document_id)

    if not chunks:
        raise ValueError("No chunks could be created from the extracted text.")

    # 3. Generate embeddings
    chunk_texts = [c["chunk_text"] for c in chunks]
    embeddings = embed_texts(chunk_texts)

    # 4. Store in vector DB with metadata
    metadata_list = [
        {
            "document_id": document_id,
            "filename": filename,
            "page_number": c["page_number"],
            "chunk_text": c["chunk_text"],
            "chunk_id": c["chunk_id"],
        }
        for c in chunks
    ]
    vector_store.add_documents(embeddings, metadata_list)

    return {
        "document_id": document_id,
        "filename": filename,
        "num_chunks": len(chunks),
    }


def query(question: str, chat_history: list[dict] | None = None) -> dict:
    """
    Answer a question using RAG: embed query → retrieve → generate.

    Args:
        question: User's question.
        chat_history: Optional list of previous messages for context.

    Returns:
        Dict with 'answer' and 'sources'.
    """
    # 1. Embed the query
    query_emb = embed_query(question)

    # 2. Retrieve top-k relevant chunks
    results = vector_store.search(query_emb, top_k=5)

    if not results:
        return {
            "answer": "No documents have been uploaded yet. Please upload a PDF first.",
            "sources": [],
        }

    # 3. Build context from retrieved chunks
    context_parts = []
    sources = []
    seen_texts = set()

    for r in results:
        chunk_text = r["chunk_text"]
        if chunk_text not in seen_texts:
            seen_texts.add(chunk_text)
            page = r["page_number"]
            filename = r.get("filename", "Unknown")
            context_parts.append(f"[{filename} - Page {page}]:\n{chunk_text}")
            sources.append({
                "page": page,
                "text": chunk_text[:300] + ("..." if len(chunk_text) > 300 else ""),
                "filename": filename,
            })

    context = "\n\n---\n\n".join(context_parts)

    # 4. Build conversation for Gemini
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=SYSTEM_PROMPT,
    )

    # Build history from chat_history for follow-up support
    history = []
    if chat_history:
        for msg in chat_history[-6:]:  # Keep last 6 messages for context
            role = msg.get("role", "user")
            gemini_role = "user" if role == "user" else "model"
            history.append({"role": gemini_role, "parts": [msg["content"]]})

    chat = model.start_chat(history=history)

    # 5. Send prompt with context
    user_message = QA_PROMPT_TEMPLATE.format(context=context, question=question)
    response = chat.send_message(user_message)

    answer = response.text

    return {
        "answer": answer,
        "sources": sources,
    }


def summarize_documents() -> dict:
    """
    Summarize all uploaded documents.

    Returns:
        Dict with 'answer' (summary) and 'sources'.
    """
    all_docs = vector_store.get_all_documents()

    if not all_docs:
        return {
            "answer": "No documents have been uploaded yet.",
            "sources": [],
        }

    # Gather chunks from all documents (limit to avoid token overflow)
    all_chunks = []
    sources = []
    for doc_id in all_docs:
        doc_chunks = vector_store.get_document_chunks(doc_id)
        for c in doc_chunks[:20]:  # Limit per document
            all_chunks.append(c["chunk_text"])
            sources.append({
                "page": c["page_number"],
                "text": c["chunk_text"][:200] + "...",
                "filename": c.get("filename", "Unknown"),
            })

    # Limit total context
    context = "\n\n".join(all_chunks[:30])

    prompt = SUMMARY_PROMPT.format(context=context)

    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction="You are an AI assistant that summarizes documents accurately and concisely.",
    )
    response = model.generate_content(prompt)

    return {
        "answer": response.text,
        "sources": sources[:5],
    }
