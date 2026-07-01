"""Tests for file service."""

import time

from app.services.file_service import (
    ensure_upload_dir,
    remove_expired_files,
    save_upload,
)


def test_save_upload_creates_file(tmp_path, monkeypatch):
    """save_upload should write file with timestamp prefix."""
    # Use tmp_path as upload dir
    import app.services.file_service as fs

    monkeypatch.setattr(fs, "UPLOAD_DIR", tmp_path)

    path = save_upload(b"hello pdf", "test.pdf")
    assert path.exists()
    assert path.read_bytes() == b"hello pdf"
    assert "test.pdf" in path.name


def test_ensure_upload_dir_creates(tmp_path, monkeypatch):
    """ensure_upload_dir should create dir if missing."""
    import app.services.file_service as fs

    new_dir = tmp_path / "nested" / "uploads"
    monkeypatch.setattr(fs, "UPLOAD_DIR", new_dir)

    result = ensure_upload_dir()
    assert result == new_dir
    assert new_dir.is_dir()


def test_remove_expired_files(tmp_path):
    """Expired files should be removed; fresh files kept."""
    f1 = tmp_path / "old.txt"
    f1.write_text("old")
    # Make it look old
    old_time = time.time() - 3600  # 1 hour ago
    import os

    os.utime(str(f1), (old_time, old_time))

    f2 = tmp_path / "new.txt"
    f2.write_text("new")
    # default mtime is now — should NOT be removed

    removed = remove_expired_files(tmp_path, max_age_seconds=1800)  # 30 min
    assert removed == 1
    assert not f1.exists()
    assert f2.exists()


def test_remove_expired_files_missing_dir(tmp_path):
    """Missing directory should return 0 removed."""
    removed = remove_expired_files(tmp_path / "nonexistent", 1800)
    assert removed == 0


def test_ensure_upload_dir_default_path():
    """ensure_upload_dir should work with default UPLOAD_DIR."""
    import app.services.file_service as fs

    result = fs.ensure_upload_dir()
    assert result == fs.UPLOAD_DIR
    assert fs.UPLOAD_DIR.is_dir()
