"""PDF upload and OCR conversion endpoints."""

import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.file_service import save_upload
from app.services.ocr_service import pdf_to_markdown

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["upload"])

ALLOWED_CONTENT_TYPES = {"application/pdf"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF file, run OCR, return Markdown."""
    # Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型 '{file.content_type}'，仅接受 PDF 文件",
        )

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"文件大小 {len(content) / 1024 / 1024:.1f}MB 超过上限 (50MB)",
        )

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="文件为空，请上传有效的 PDF 文件")

    # Validate PDF header magic bytes
    if not content.startswith(b"%PDF"):
        raise HTTPException(
            status_code=400,
            detail="文件不是有效的 PDF 格式，请检查文件是否损坏",
        )

    # Save file to temp directory
    saved_path = save_upload(content, file.filename or "upload.pdf")
    logger.info(f"Saved upload: {saved_path}")

    # Run OCR
    try:
        markdown = await pdf_to_markdown(str(saved_path))
    except Exception as exc:
        logger.error(f"OCR failed for {saved_path}: {exc}")
        raise HTTPException(
            status_code=500,
            detail=f"OCR 处理失败: {str(exc)}",
        )

    return {
        "filename": file.filename,
        "markdown": markdown,
    }
