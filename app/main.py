"""
FastAPI application entry point for df_ocr.
Serves the frontend static files and API routes.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import download, health, upload
from app.services.file_service import cleanup_expired_files

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Ensure upload temp directory exists
    upload_dir = Path("/tmp/df_ocr/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Start background cleanup task
    cleanup_task = asyncio.create_task(cleanup_expired_files())
    logger.info("Background cleanup task started")

    yield

    # Shutdown
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    logger.info("Application shut down")


app = FastAPI(
    title="df_ocr",
    description="PDF OCR to Markdown using PP-StructureV3",
    version="0.1.0",
    lifespan=lifespan,
)

# API routes
app.include_router(health.router)
app.include_router(upload.router)
app.include_router(download.router)

# Static frontend (must be last to not shadow API routes)
static_dir = Path(__file__).parent / "static"
if static_dir.is_dir():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
