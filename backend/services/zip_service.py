import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

MAX_ZIP_BYTES = 25 * 1024 * 1024
MAX_TOTAL_SIZE_BYTES = 100 * 1024 * 1024
MAX_FILES = 200

BASE_STORAGE_DIR = Path(__file__).resolve().parents[2] / "storage" / "uploads"


def save_and_extract_zip(upload: UploadFile) -> Path:
    if not upload.filename or not upload.filename.lower().endswith(".zip"):
        raise ValueError("Only .zip files are supported")

    BASE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    upload_id = f"{timestamp}-{uuid4().hex}"
    upload_dir = BASE_STORAGE_DIR / upload_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    zip_path = upload_dir / "upload.zip"
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

    extract_dir = upload_dir / "extracted"
    extract_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as archive:
        members = archive.infolist()
        if len(members) > MAX_FILES:
            raise ValueError("ZIP contains too many files")

        total_uncompressed = 0
        for member in members:
            if member.is_dir():
                continue
            total_uncompressed += member.file_size
            if total_uncompressed > MAX_TOTAL_SIZE_BYTES:
                raise ValueError("Extracted contents exceed size limit")

            target_path = extract_dir / member.filename
            resolved_target = target_path.resolve()
            if extract_dir not in resolved_target.parents and resolved_target != extract_dir:
                raise ValueError("ZIP contains invalid paths")

            resolved_target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as source, resolved_target.open("wb") as dest:
                shutil.copyfileobj(source, dest)

    return extract_dir
