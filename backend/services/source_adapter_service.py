import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote, urlsplit

import httpx
from fastapi import UploadFile

from services.archive_service import (
    cleanup_workspace,
    create_source_workspace,
    extract_zip_archive,
)
from services.zip_service import save_and_extract_zip


MAX_GITHUB_ARCHIVE_BYTES = 25 * 1024 * 1024
GITHUB_REQUEST_TIMEOUT_SECONDS = 30.0
GITHUB_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


@dataclass(frozen=True)
class SourceMetadata:
    source_type: str
    source_locator: str
    source_ref: str | None = None
    source_commit: str | None = None


@dataclass(frozen=True)
class PreparedProjectSource:
    project_root: Path
    metadata: SourceMetadata


def prepare_local_source(root_path: str) -> PreparedProjectSource:
    return PreparedProjectSource(
        project_root=Path(root_path),
        metadata=SourceMetadata(
            source_type="local",
            source_locator=root_path,
        ),
    )


def prepare_zip_source(upload: UploadFile) -> PreparedProjectSource:
    project_root = save_and_extract_zip(upload)
    return PreparedProjectSource(
        project_root=project_root,
        metadata=SourceMetadata(
            source_type="zip",
            source_locator=upload.filename or "upload.zip",
        ),
    )


def prepare_github_source(
    repository_url: str,
    ref: str | None = None,
) -> PreparedProjectSource:
    owner, repository, canonical_url = parse_github_repository_url(repository_url)
    normalized_ref = ref.strip() if ref and ref.strip() else None
    archive_url = f"https://api.github.com/repos/{owner}/{repository}/zipball"
    if normalized_ref:
        archive_url = f"{archive_url}/{quote(normalized_ref, safe='')}"

    workspace = create_source_workspace("github")
    try:
        archive_path = workspace / "repository.zip"
        download_github_archive(archive_url, archive_path)
        project_root = extract_zip_archive(archive_path, workspace)
        normalized_root = workspace / repository
        if project_root != normalized_root:
            project_root.rename(normalized_root)
            project_root = normalized_root
    except Exception:
        cleanup_workspace(workspace)
        raise

    return PreparedProjectSource(
        project_root=project_root,
        metadata=SourceMetadata(
            source_type="github",
            source_locator=canonical_url,
            source_ref=normalized_ref,
        ),
    )


def parse_github_repository_url(repository_url: str) -> tuple[str, str, str]:
    value = repository_url.strip()
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() != "github.com":
        raise ValueError("Enter a valid public GitHub repository URL")
    if parsed.query or parsed.fragment or parsed.username or parsed.password:
        raise ValueError("Enter a canonical GitHub repository URL")

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) != 2:
        raise ValueError("GitHub URL must use the format github.com/owner/repository")

    owner, repository = parts
    if repository.lower().endswith(".git"):
        repository = repository[:-4]
    if not owner or not repository:
        raise ValueError("GitHub URL must include an owner and repository")
    if not GITHUB_NAME_PATTERN.fullmatch(owner) or not GITHUB_NAME_PATTERN.fullmatch(
        repository
    ):
        raise ValueError("GitHub URL contains invalid owner or repository characters")

    canonical_url = f"https://github.com/{owner}/{repository}"
    return owner, repository, canonical_url


def download_github_archive(url: str, destination: Path) -> None:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "CodeForge-AI",
    }
    try:
        with httpx.stream(
            "GET",
            url,
            headers=headers,
            follow_redirects=True,
            timeout=GITHUB_REQUEST_TIMEOUT_SECONDS,
        ) as response:
            if response.status_code == 404:
                raise ValueError("GitHub repository or ref was not found")
            if response.status_code >= 400:
                raise ValueError(
                    f"GitHub archive download failed with status {response.status_code}"
                )

            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > MAX_GITHUB_ARCHIVE_BYTES:
                raise ValueError("GitHub repository archive exceeds size limit")

            total_bytes = 0
            with destination.open("wb") as handle:
                for chunk in response.iter_bytes(1024 * 1024):
                    total_bytes += len(chunk)
                    if total_bytes > MAX_GITHUB_ARCHIVE_BYTES:
                        raise ValueError("GitHub repository archive exceeds size limit")
                    handle.write(chunk)
    except httpx.HTTPError as exc:
        raise ValueError("Unable to download the GitHub repository") from exc
