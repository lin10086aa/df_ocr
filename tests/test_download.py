"""Tests for download endpoints."""

import io
import zipfile

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


async def test_zip_download_single_file(client: AsyncClient):
    """ZIP download with one file should return a valid zip."""
    payload = {
        "files": [
            {"filename": "report.pdf", "markdown": "# Hello\n\nWorld"},
        ]
    }
    resp = await client.post("/api/download/zip", json=payload)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/zip"

    # Verify zip content
    buf = io.BytesIO(resp.read())
    with zipfile.ZipFile(buf) as zf:
        names = zf.namelist()
        assert "report.md" in names
        content = zf.read("report.md").decode("utf-8")
        assert "# Hello" in content


async def test_zip_download_multiple_files(client: AsyncClient):
    """ZIP download with multiple files should include all .md files."""
    payload = {
        "files": [
            {"filename": "a.pdf", "markdown": "# A"},
            {"filename": "b.pdf", "markdown": "# B"},
        ]
    }
    resp = await client.post("/api/download/zip", json=payload)
    assert resp.status_code == 200

    buf = io.BytesIO(resp.read())
    with zipfile.ZipFile(buf) as zf:
        names = zf.namelist()
        assert "a.md" in names
        assert "b.md" in names


async def test_zip_download_duplicate_filenames(client: AsyncClient):
    """Duplicate filenames should be disambiguated."""
    payload = {
        "files": [
            {"filename": "doc.pdf", "markdown": "# First"},
            {"filename": "doc.pdf", "markdown": "# Second"},
        ]
    }
    resp = await client.post("/api/download/zip", json=payload)
    assert resp.status_code == 200

    buf = io.BytesIO(resp.read())
    with zipfile.ZipFile(buf) as zf:
        names = zf.namelist()
        assert len(names) == 2
        assert "doc.md" in names
        assert "doc (1).md" in names


async def test_zip_download_empty_files_rejected(client: AsyncClient):
    """Empty file list should be rejected with validation error."""
    resp = await client.post("/api/download/zip", json={"files": []})
    assert resp.status_code == 422  # Pydantic validation error
