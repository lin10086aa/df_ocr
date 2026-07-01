"""Tests for upload endpoint."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def client():
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# A minimal valid PDF (1 blank page)
MINIMAL_PDF = (
    b"%PDF-1.4\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\n"
    b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n"
    b"trailer<</Size 4/Root 1 0 R>>\n"
    b"startxref\n190\n%%EOF"
)


async def test_upload_rejects_non_pdf(client: AsyncClient):
    """Uploading a PNG file should return 400."""
    resp = await client.post(
        "/api/upload",
        files={"file": ("test.png", b"\x89PNG\r\n\x1a\nfake", "image/png")},
    )
    assert resp.status_code == 400
    data = resp.json()
    assert "不支持" in data["detail"]


async def test_upload_rejects_empty_file(client: AsyncClient):
    """Uploading an empty file should return 400."""
    resp = await client.post(
        "/api/upload",
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )
    assert resp.status_code == 400


async def test_upload_rejects_invalid_pdf_magic(client: AsyncClient):
    """Uploading something claiming to be PDF but without valid magic bytes."""
    resp = await client.post(
        "/api/upload",
        files={"file": ("fake.pdf", b"not a pdf", "application/pdf")},
    )
    assert resp.status_code == 400
    data = resp.json()
    assert "PDF 格式" in data["detail"]


async def test_upload_accepts_valid_pdf(client: AsyncClient):
    """Uploading a valid minimal PDF should return 200 with markdown placeholder."""
    resp = await client.post(
        "/api/upload",
        files={"file": ("doc.pdf", MINIMAL_PDF, "application/pdf")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "doc.pdf"
    assert "markdown" in data
    # With mock engine, we expect a placeholder string
    assert len(data["markdown"]) > 0


async def test_upload_rejects_oversized_file(client: AsyncClient, monkeypatch):
    """File exceeding size limit should return 413."""
    # Lower the limit for testing
    monkeypatch.setattr("app.routers.upload.MAX_FILE_SIZE", 4)

    content = b"%PDF-1.4\n" + b"x" * 100
    resp = await client.post(
        "/api/upload",
        files={"file": ("big.pdf", content, "application/pdf")},
    )
    assert resp.status_code == 413
    assert "上限" in resp.json()["detail"]
