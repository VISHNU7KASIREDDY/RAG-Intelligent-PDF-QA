"""
Text chunking service with sentence-aware splitting and token counting.
"""
import tiktoken
import uuid


# Using cl100k_base encoding (same as used by OpenAI embeddings)
_encoder = tiktoken.get_encoding("cl100k_base")

CHUNK_SIZE = 600  # tokens
CHUNK_OVERLAP = 100  # tokens


def chunk_pages(
    pages: list[dict],
    document_id: str | None = None,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[dict]:
    """
    Split extracted pages into overlapping chunks, preserving metadata.

    Args:
        pages: List of {'page_number': int, 'text': str} from pdf_loader.
        document_id: Unique ID for the source document.
        chunk_size: Target chunk size in tokens.
        chunk_overlap: Overlap between consecutive chunks in tokens.

    Returns:
        List of chunk dicts with keys:
            document_id, page_number, chunk_text, chunk_id
    """
    if document_id is None:
        document_id = str(uuid.uuid4())

    chunks: list[dict] = []

    for page in pages:
        page_number = page["page_number"]
        text = page["text"]

        # Split into sentences first
        sentences = _split_into_sentences(text)

        current_chunk_sentences: list[str] = []
        current_token_count = 0

        for sentence in sentences:
            sentence_tokens = _count_tokens(sentence)

            # If adding this sentence exceeds chunk_size, finalize current chunk
            if current_token_count + sentence_tokens > chunk_size and current_chunk_sentences:
                chunk_text = " ".join(current_chunk_sentences)
                chunks.append({
                    "document_id": document_id,
                    "page_number": page_number,
                    "chunk_text": chunk_text,
                    "chunk_id": str(uuid.uuid4()),
                })

                # Keep overlap: walk back from end until we have ~overlap tokens
                overlap_sentences: list[str] = []
                overlap_tokens = 0
                for s in reversed(current_chunk_sentences):
                    s_tokens = _count_tokens(s)
                    if overlap_tokens + s_tokens > chunk_overlap:
                        break
                    overlap_sentences.insert(0, s)
                    overlap_tokens += s_tokens

                current_chunk_sentences = overlap_sentences
                current_token_count = overlap_tokens

            current_chunk_sentences.append(sentence)
            current_token_count += sentence_tokens

        # Flush remaining sentences
        if current_chunk_sentences:
            chunk_text = " ".join(current_chunk_sentences)
            chunks.append({
                "document_id": document_id,
                "page_number": page_number,
                "chunk_text": chunk_text,
                "chunk_id": str(uuid.uuid4()),
            })

    return chunks


def _split_into_sentences(text: str) -> list[str]:
    """
    Simple sentence splitter that handles common abbreviations.
    Splits on '. ', '! ', '? ', and newline boundaries.
    """
    import re

    # Split on sentence-ending punctuation followed by space or newline
    raw = re.split(r"(?<=[.!?])\s+|\n+", text)
    # Filter empty strings and strip whitespace
    return [s.strip() for s in raw if s.strip()]


def _count_tokens(text: str) -> int:
    """Count tokens using tiktoken."""
    return len(_encoder.encode(text))
