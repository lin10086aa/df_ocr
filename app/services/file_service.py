"""File management: save uploads, periodic cleanup."""

import asyncio
import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("/tmp/df_ocr/uploads")
MAX_AGE_SECONDS = 30 * 60  # 30 minutes


def ensure_upload_dir() -> Path:
    """Create upload directory if it doesn't exist and return path."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    return UPLOAD_DIR


def save_upload(file_content: bytes, filename: str) -> Path:
    """Save uploaded file to temp directory. Returns file path."""
    ensure_upload_dir()
    ts = int(time.time() * 1000)
    safe_name = f"{ts}_{filename}"
    file_path = UPLOAD_DIR / safe_name
    file_path.write_bytes(file_content)
    return file_path


def remove_expired_files(directory: Path, max_age_seconds: int) -> int:
    """Remove files older than max_age_seconds. Returns count of removed files."""
    if not directory.is_dir():
        return 0
    now = time.time()
    removed = 0
    for f in directory.iterdir():
        if f.is_file():
            age = now - f.stat().st_mtime
            if age > max_age_seconds:
                f.unlink()
                removed += 1
                logger.info(f"Cleaned up expired file: {f.name}")
    return removed


async def cleanup_expired_files():
    """Background task: periodically remove expired files."""
    while True:
        await asyncio.sleep(300)  # Every 5 minutes
        try:
            ensure_upload_dir()
            removed = remove_expired_files(UPLOAD_DIR, MAX_AGE_SECONDS)
            if removed:
                logger.info(f"Cleanup removed {removed} file(s)")
        except Exception as exc:
            logger.warning(f"Cleanup error: {exc}")
