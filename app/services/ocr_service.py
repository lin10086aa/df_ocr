"""OCR service: PDF to Markdown via PP-StructureV3."""

import logging
from pathlib import Path
from typing import Protocol

logger = logging.getLogger(__name__)


# ── Engine interface ──────────────────────────────────────────


class OcrEngine(Protocol):
    """Protocol for OCR engines."""

    def process_pdf(self, pdf_path: str) -> str:
        """Convert PDF to Markdown string."""
        ...


# ── Mock engine (for testing / fallback) ─────────────────────


class _MockEngine:
    """Mock engine — returns placeholder text. Used when PaddleOCR is unavailable."""

    def process_pdf(self, pdf_path: str) -> str:
        path = Path(pdf_path)
        return (
            f"# OCR 结果（占位符）\n\n"
            f"文件名: {path.name}\n\n"
            f"*PP-StructureV3 未安装或未就绪，此处为模拟输出。*"
        )


# ── PP-StructureV3 engine ────────────────────────────────────


class _PPStructureEngine:  # pragma: no cover — requires PaddleOCR + poppler runtime
    """Real PP-StructureV3 OCR engine."""

    def __init__(self):
        from paddleocr import PPStructure

        self._engine = PPStructure(table=True, ocr=True, show_log=False)
        logger.info("PP-StructureV3 engine initialized")

    def process_pdf(self, pdf_path: str) -> str:
        from pdf2image import convert_from_path

        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        images = convert_from_path(pdf_path, dpi=300)
        logger.info(f"PDF has {len(images)} page(s)")

        if not images:
            raise ValueError("PDF 文件无页面内容，无法进行 OCR")

        all_parts: list[str] = []
        for i, image in enumerate(images):
            logger.info(f"OCR page {i + 1}/{len(images)}")
            result = self._engine(image)
            if result:
                text = self._extract_markdown(result)
                if text:
                    all_parts.append(text)

        return "\n\n".join(all_parts)

    @staticmethod
    def _extract_markdown(ocr_results: list[dict]) -> str:
        """Extract markdown text from PP-StructureV3 results."""
        lines: list[str] = []
        for item in ocr_results:
            item_type = item.get("type", "")
            if item_type == "table":
                # Table result: render as markdown table
                html = item.get("html", "")
                if html:
                    lines.append(_html_table_to_markdown(html))
                    continue
            # Text / title / figure text
            text = ""
            for block in item.get("res", []):
                text += block.get("text", "")
            if text.strip():
                lines.append(text)
        return "\n\n".join(lines)


def _html_table_to_markdown(html: str) -> str:
    """Convert a simple HTML table to Markdown table syntax."""
    import re

    rows: list[list[str]] = []
    for tr in re.findall(r"<tr>(.*?)</tr>", html, re.DOTALL | re.IGNORECASE):
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.DOTALL | re.IGNORECASE)
        rows.append([re.sub(r"<[^>]+>", "", c).strip() for c in cells])

    if not rows:
        return html

    md_lines: list[str] = []
    # Header
    md_lines.append("| " + " | ".join(rows[0]) + " |")
    md_lines.append("| " + " | ".join(["---"] * len(rows[0])) + " |")
    # Body
    for row in rows[1:]:
        # Pad shorter rows
        while len(row) < len(rows[0]):
            row.append("")
        md_lines.append("| " + " | ".join(row) + " |")

    return "\n".join(md_lines)


# ── Engine factory ────────────────────────────────────────────

_engine: OcrEngine | None = None


def get_engine() -> OcrEngine:
    """Lazy-load OCR engine. Falls back to mock if PaddleOCR unavailable."""
    global _engine
    if _engine is not None:
        return _engine

    try:
        _engine = _PPStructureEngine()
    except ImportError as e:
        logger.warning(f"PaddleOCR not available ({e}), using mock engine")
        _engine = _MockEngine()
    except Exception as e:
        logger.warning(f"PP-StructureV3 init failed ({e}), using mock engine")
        _engine = _MockEngine()

    return _engine


# ── Public API ────────────────────────────────────────────────


async def pdf_to_markdown(pdf_path: str) -> str:
    """Convert a PDF file to Markdown using the configured OCR engine."""
    engine = get_engine()
    # Offload CPU-bound work to thread
    import asyncio

    return await asyncio.to_thread(engine.process_pdf, pdf_path)
