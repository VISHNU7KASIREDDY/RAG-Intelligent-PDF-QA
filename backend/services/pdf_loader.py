"""
PDF text extraction service using PyMuPDF (fitz).
"""
import fitz  # PyMuPDF
import re


def extract_text_from_pdf(file_bytes: bytes) -> list[dict]:
    """
    Extract text from a PDF file, preserving page boundaries.

    Args:
        file_bytes: Raw bytes of the PDF file.

    Returns:
        List of dicts with 'page_number' and 'text' keys.
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        raw_text = page.get_text("text")

        # Clean the text
        cleaned = _clean_text(raw_text)

        if cleaned.strip():
            pages.append({
                "page_number": page_num + 1,  # 1-indexed
                "text": cleaned,
            })

    doc.close()
    return pages


def _clean_text(text: str) -> str:
    """Remove noise characters and normalize whitespace."""
    # Replace multiple spaces with single space
    text = re.sub(r"[ \t]+", " ", text)
    # Replace 3+ newlines with 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Remove non-printable characters (keep newlines, tabs, standard chars)
    text = re.sub(r"[^\x20-\x7E\n\t]", "", text)
    return text.strip()
