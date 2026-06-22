import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


MAX_ARCHIVE_FILES = 2_000
MAX_EXTRACTED_SIZE_BYTES = 100 * 1024 * 1024

BASE_STORAGE_DIR = Path(__file__).resolve().parents[2] / "storage"


def create_source_workspace(source_type: str) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    workspace = (
        BASE_STORAGE_DIR
        / source_type
        / f"{timestamp}-{uuid4().hex}"
    )
    workspace.mkdir(parents=True, exist_ok=False)
    return workspace


def extract_zip_archive(zip_path: Path, workspace: Path) -> Path:
    extract_dir = workspace / "extracted"
    extract_dir.mkdir(parents=True, exist_ok=False)

    try:
        with zipfile.ZipFile(zip_path, "r") as archive:
            members = archive.infolist()
            if len(members) > MAX_ARCHIVE_FILES:
                raise ValueError("ZIP contains too many files")

            total_uncompressed = 0
            for member in members:
                if member.is_dir():
                    continue

                total_uncompressed += member.file_size
                if total_uncompressed > MAX_EXTRACTED_SIZE_BYTES:
                    raise ValueError("Extracted contents exceed size limit")

                target_path = extract_dir / member.filename
                resolved_target = target_path.resolve()
                if (
                    extract_dir not in resolved_target.parents
                    and resolved_target != extract_dir
                ):
                    raise ValueError("ZIP contains invalid paths")

                resolved_target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as source, resolved_target.open("wb") as dest:
                    shutil.copyfileobj(source, dest)
    except (OSError, zipfile.BadZipFile) as exc:
        raise ValueError("ZIP file is invalid or could not be extracted") from exc

    return find_project_root(extract_dir)


def find_project_root(extract_dir: Path) -> Path:
    children = list(extract_dir.iterdir())
    if len(children) == 1 and children[0].is_dir():
        return children[0]
    return extract_dir


def cleanup_workspace(workspace: Path) -> None:
    shutil.rmtree(workspace, ignore_errors=True)
