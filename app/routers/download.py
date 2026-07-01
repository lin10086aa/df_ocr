"""Download endpoints: single .md and batch .zip."""

import io
import zipfile

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/download", tags=["download"])


class FileItem(BaseModel):
    """A single file entry for batch download."""

    filename: str = Field(..., description="Original PDF filename")
    markdown: str = Field(..., description="OCR Markdown result")


class ZipRequest(BaseModel):
    """Request body for batch zip download."""

    files: list[FileItem] = Field(..., min_length=1, max_length=10)


@router.post("/zip")
async def download_zip(req: ZipRequest):
    """Receive a list of {filename, markdown} and return a .zip file."""
    buf = io.BytesIO()
    seen: set[str] = set()

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for item in req.files:
            # Derive .md filename, avoid duplicates
            base = item.filename
            if base.lower().endswith(".pdf"):
                base = base[:-4]
            md_name = base + ".md"

            # Handle duplicates
            unique = md_name
            counter = 1
            while unique in seen:
                unique = f"{base} ({counter}).md"
                counter += 1
            seen.add(unique)

            zf.writestr(unique, item.markdown.encode("utf-8"))

    buf.seek(0)

    # Return as streaming response
    from fastapi.responses import StreamingResponse

    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=ocr_results.zip"},
    )
