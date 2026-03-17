"""
Upload route for PDF file processing.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from models.schemas import UploadResponse
from services.rag_pipeline import process_pdf

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file, extract text, generate embeddings, and store in vector DB.
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted. Please upload a .pdf file.",
        )

    try:
        file_bytes = await file.read()

        if len(file_bytes) == 0:
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")

        result = process_pdf(file_bytes, file.filename)

        return UploadResponse(
            document_id=result["document_id"],
            filename=result["filename"],
            num_chunks=result["num_chunks"],
            message=f"Successfully processed '{file.filename}' into {result['num_chunks']} chunks.",
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}",
        )
