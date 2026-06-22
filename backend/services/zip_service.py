from pathlib import Path

from fastapi import UploadFile

from services.archive_service import (
    cleanup_workspace,
    create_source_workspace,
    extract_zip_archive,
)

MAX_ZIP_BYTES = 25 * 1024 * 1024


def save_and_extract_zip(upload: UploadFile) -> Path:
    if not upload.filename or not upload.filename.lower().endswith(".zip"):
        raise ValueError("Only .zip files are supported")

    workspace = create_source_workspace("uploads")
    try:
        zip_path = workspace / "upload.zip"
        total_bytes = 0
        with zip_path.open("wb") as handle:
            while True:
                chunk = upload.file.read(1024 * 1024)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if total_bytes > MAX_ZIP_BYTES:
                    raise ValueError("ZIP file exceeds size limit")
                handle.write(chunk)

        return extract_zip_archive(zip_path, workspace)
    except Exception:
        cleanup_workspace(workspace)
        raise
