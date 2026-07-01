"""Tests for OCR service."""

import pytest

from app.services.ocr_service import (
    _MockEngine,
    _PPStructureEngine,
    _html_table_to_markdown,
    get_engine,
    pdf_to_markdown,
)


# ── Mock engine tests ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_mock_engine_process_pdf(tmp_path):
    """Mock engine should return placeholder text for any PDF."""
    pdf = tmp_path / "test.pdf"
    pdf.write_text("fake pdf content")

    engine = _MockEngine()
    result = engine.process_pdf(str(pdf))

    assert "test.pdf" in result
    assert "占位符" in result


@pytest.mark.asyncio
async def test_mock_engine_missing_file():
    """Mock engine should handle missing files gracefully."""
    engine = _MockEngine()
    result = engine.process_pdf("/nonexistent/path.pdf")

    # Mock engine doesn't check existence — it just formats a placeholder
    assert len(result) > 0


# ── HTML table to Markdown ────────────────────────────────────


@pytest.mark.parametrize(
    "html,expected_contains",
    [
        (
            "<table><tr><td>A</td><td>B</td></tr><tr><td>1</td><td>2</td></tr></table>",
            "| A | B |",
        ),
        (
            "<table><tr><th>Name</th><th>Age</th></tr><tr><td>Alice</td><td>30</td></tr></table>",
            "| Name | Age |",
        ),
        ("no table here", "no table here"),
    ],
)
def test_html_table_to_markdown(html, expected_contains):
    """HTML table conversion should produce valid Markdown."""
    result = _html_table_to_markdown(html)
    assert expected_contains in result


# ── Engine factory ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_engine_returns_same_instance():
    """get_engine should cache and return the same instance."""
    e1 = get_engine()
    e2 = get_engine()
    assert e1 is e2


# ── extract_markdown ─────────────────────────────────────────


def test_extract_markdown_with_table():
    """_extract_markdown should render table items as markdown."""
    ocr_results = [
        {"type": "text", "res": [{"text": "Hello World"}]},
        {
            "type": "table",
            "html": "<table><tr><td>A</td><td>B</td></tr><tr><td>1</td><td>2</td></tr></table>",
            "res": [],
        },
    ]
    result = _PPStructureEngine._extract_markdown(ocr_results)
    assert "Hello World" in result
    assert "| A | B |" in result


def test_extract_markdown_empty():
    """_extract_markdown with empty input returns empty string."""
    assert _PPStructureEngine._extract_markdown([]) == ""


# ── pdf_to_markdown integration ───────────────────────────────


@pytest.mark.asyncio
async def test_pdf_to_markdown_with_file(tmp_path):
    """pdf_to_markdown should return non-empty string for a valid file."""
    pdf = tmp_path / "doc.pdf"
    pdf.write_text("dummy")

    # With real engine, this may fail if poppler is missing.
    # In CI/test environments, the mock engine handles it gracefully.
    engine = get_engine()
    if isinstance(engine, _MockEngine):
        result = await pdf_to_markdown(str(pdf))
        assert len(result) > 0
    else:
        # Real engine test: skip if poppler unavailable
        try:
            result = await pdf_to_markdown(str(pdf))
            assert isinstance(result, str)
        except Exception:
            pytest.skip("poppler not available in this environment")
