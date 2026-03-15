from fastapi import APIRouter, UploadFile, File
import shutil
import os
from services.cv_parser import extract_pdf_text, extract_docx_text, parse_cv_text

router = APIRouter(prefix="/cv", tags=["CV Parser"])

@router.post("/upload-cv")
async def upload_cv(file: UploadFile = File(...)):

    os.makedirs("uploads", exist_ok=True)
    
    file_path = f"uploads/{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if file.filename.endswith(".pdf"):
        text = extract_pdf_text(file_path)
    
    elif file.filename.endswith(".docx"):
        text = extract_docx_text(file_path)
    
    else:
        return{"error": "Upload only PDF or DOCX file"}
    
    parsed_data = parse_cv_text(text)
    
    return{
        "Message": "CV processed successfully",
        "data": parsed_data
    }
