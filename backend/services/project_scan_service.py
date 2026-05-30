from __future__ import annotations

import json
import os
from collections import defaultdict
from pathlib import Path

from models.project import (
    DatabaseSignal,
    DirectorySummary,
    FileClassification,
    FrameworkSignal,
    ProjectMap,
)

MAX_DEPTH = 5
MAX_FILES = 200
MAX_FILE_SIZE_BYTES = 1 * 1024 * 1024
MAX_TOTAL_SIZE_BYTES = 25 * 1024 * 1024
MAX_CONTENT_READ_BYTES = 64 * 1024

IGNORE_DIRS = {
    "node_modules",
    "venv",
    ".env",
    ".git",
    "dist",
    "build",
    "coverage",
    "__pycache__",
    ".next",
    "target",
    "out",
}

EXCLUDED_CONTENT_PATHS = {
    "backend/services/project_scan_service.py",
}

ALLOWED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".go",
    ".rs",
    ".cpp",
    ".c",
    ".cs",
    ".html",
    ".css",
    ".scss",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".md",
    ".sql",
}

ALLOWED_FILENAMES = {
    "readme",
    "readme.md",
    "readme.txt",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "requirements.txt",
    "pyproject.toml",
    "pipfile",
    "poetry.lock",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "go.mod",
    "cargo.toml",
    "composer.json",
    "gemfile",
    ".env.example",
    ".env.sample",
}

PACKAGE_MANAGER_FILES = {
    "package.json": "npm",
    "package-lock.json": "npm",
    "yarn.lock": "yarn",
    "pnpm-lock.yaml": "pnpm",
    "requirements.txt": "pip",
    "pyproject.toml": "pip",
    "pipfile": "pipenv",
    "poetry.lock": "poetry",
    "pom.xml": "maven",
    "build.gradle": "gradle",
    "build.gradle.kts": "gradle",
    "go.mod": "go",
    "cargo.toml": "cargo",
    "composer.json": "composer",
    "gemfile": "bundler",
}

ENTRY_POINT_NAMES = {
    "main.py",
    "app.py",
    "server.py",
    "main.js",
    "index.js",
    "server.js",
    "main.ts",
    "index.ts",
    "main.jsx",
    "index.jsx",
    "main.tsx",
    "index.tsx",
}

IMPORTANT_FILES = {
    "readme",
    "readme.md",
    "readme.txt",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    ".env.example",
    ".env.sample",
    "config.json",
    "config.yaml",
    "config.yml",
    "settings.py",
    "appsettings.json",
}

EXTENSION_LANGUAGE = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".java": "Java",
    ".go": "Go",
    ".rs": "Rust",
    ".cpp": "C++",
    ".c": "C",
    ".cs": "C#",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
    ".md": "Markdown",
    ".sql": "SQL",
}

ALLOWED_DB_SIGNAL_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".go",
    ".rs",
    ".cpp",
    ".c",
    ".cs",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".sql",
}

DATABASE_KEYWORDS = {
    "sqlite": "SQLite",
    "postgres": "PostgreSQL",
    "psycopg": "PostgreSQL",
    "mysql": "MySQL",
    "mariadb": "MariaDB",
    "mongodb": "MongoDB",
    "mongoose": "MongoDB",
    "redis": "Redis",
    "prisma": "Prisma",
    "sqlalchemy": "SQLAlchemy",
}

BASE_SCAN_DIR = Path(__file__).resolve().parents[2]


def scan_project(root_path: str) -> ProjectMap:
    resolved_root = resolve_scan_path(root_path)
    project_name = resolved_root.name

    file_counts: dict[str, int] = defaultdict(int)
    total_size = 0
    scanned_files = 0

    languages: set[str] = set()
    important_files: list[str] = []
    entry_points: list[str] = []
    package_managers: set[str] = set()
    directory_counts: dict[str, int] = defaultdict(int)
    file_classifications: list[FileClassification] = []

    framework_signals: dict[str, FrameworkSignal] = {}
    database_signal_map: dict[str, set[str]] = defaultdict(set)

    stop_scanning = False

    for root, dirnames, filenames in os.walk(resolved_root):
        current_path = Path(root)
        depth = len(current_path.relative_to(resolved_root).parts)
        if depth >= MAX_DEPTH:
            dirnames.clear()
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

        for filename in filenames:
            if scanned_files >= MAX_FILES:
                stop_scanning = True
                break

            file_path = current_path / filename
            rel_path = file_path.relative_to(resolved_root).as_posix()
            file_size = file_path.stat().st_size

            if not is_allowed_file(file_path):
                continue
            if file_size > MAX_FILE_SIZE_BYTES:
                continue
            if total_size + file_size > MAX_TOTAL_SIZE_BYTES:
                stop_scanning = True
                break

            total_size += file_size
            scanned_files += 1

            extension = file_path.suffix.lower()
            file_counts["total"] += 1
            if extension:
                file_counts[extension] += 1

            language = EXTENSION_LANGUAGE.get(extension)
            if language:
                languages.add(language)

            filename_lower = filename.lower()
            if filename_lower in IMPORTANT_FILES:
                important_files.append(rel_path)

            if is_entry_point(rel_path):
                entry_points.append(rel_path)

            manager = PACKAGE_MANAGER_FILES.get(filename_lower)
            if manager:
                package_managers.add(manager)

            top_level = rel_path.split("/")[0]
            directory_counts[top_level] += 1

            category = classify_file(rel_path, extension, filename_lower)
            file_classifications.append(
                FileClassification(path=rel_path, category=category)
            )

            content = ""
            if rel_path not in EXCLUDED_CONTENT_PATHS:
                content = read_file_content(file_path)
            if content:
                detect_frameworks(
                    file_path=file_path,
                    content=content,
                    framework_signals=framework_signals,
                )
                detect_databases(
                    content=content,
                    extension=extension,
                    rel_path=rel_path,
                    database_signal_map=database_signal_map,
                )

        if stop_scanning:
            break

    directory_summary = [
        DirectorySummary(path=path, file_count=count)
        for path, count in sorted(
            directory_counts.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    ]

    framework_list = sorted(
        framework_signals.values(),
        key=lambda item: item.confidence,
        reverse=True,
    )

    frameworks = [signal.name for signal in framework_list]

    database_signals = [
        DatabaseSignal(name=name, evidence=sorted(list(evidence)))
        for name, evidence in database_signal_map.items()
    ]

    return ProjectMap(
        project_name=project_name,
        languages=sorted(languages),
        frameworks=frameworks,
        framework_confidence=framework_list,
        package_managers=sorted(package_managers),
        file_counts=dict(file_counts),
        important_files=sorted(important_files),
        entry_points=sorted(entry_points),
        directory_summary=directory_summary,
        database_signals=database_signals,
        file_classifications=file_classifications,
    )


def resolve_scan_path(root_path: str) -> Path:
    candidate = Path(root_path)
    if not candidate.is_absolute():
        candidate = (BASE_SCAN_DIR / candidate).resolve()
    else:
        candidate = candidate.resolve()

    if not candidate.exists() or not candidate.is_dir():
        raise ValueError("Scan path must be an existing directory")

    try:
        candidate.relative_to(BASE_SCAN_DIR)
    except ValueError as exc:
        raise ValueError("Scan path must be within the repository") from exc

    return candidate


def is_allowed_file(file_path: Path) -> bool:
    if file_path.is_dir():
        return False
    filename_lower = file_path.name.lower()
    extension = file_path.suffix.lower()
    if extension in ALLOWED_EXTENSIONS:
        return True
    if filename_lower in ALLOWED_FILENAMES:
        return True
    return False


def is_entry_point(rel_path: str) -> bool:
    name = Path(rel_path).name.lower()
    if name in ENTRY_POINT_NAMES:
        return True
    return False


def classify_file(rel_path: str, extension: str, filename_lower: str) -> str:
    rel_lower = rel_path.lower()
    if "test" in rel_lower or filename_lower.endswith("_test.py"):
        return "test"
    if ".spec." in rel_lower or ".test." in rel_lower:
        return "test"
    if filename_lower in IMPORTANT_FILES:
        if filename_lower.startswith("readme") or filename_lower.endswith(".md"):
            return "documentation"
        return "configuration"
    if "docs" in rel_lower or extension == ".md":
        return "documentation"
    if filename_lower in {"dockerfile", "docker-compose.yml", "docker-compose.yaml"}:
        return "build/deployment"
    if rel_lower.startswith(".github/") or "workflows" in rel_lower:
        return "build/deployment"
    if extension in {".json", ".yaml", ".yml", ".toml"}:
        return "configuration"
    if extension in EXTENSION_LANGUAGE:
        return "source"
    return "other"


def read_file_content(file_path: Path) -> str:
    try:
        with file_path.open("r", encoding="utf-8", errors="ignore") as handle:
            return handle.read(MAX_CONTENT_READ_BYTES)
    except OSError:
        return ""


def detect_frameworks(
    file_path: Path,
    content: str,
    framework_signals: dict[str, FrameworkSignal],
) -> None:
    filename_lower = file_path.name.lower()
    if filename_lower == "package.json":
        try:
            package_json = json.loads(content)
        except json.JSONDecodeError:
            return
        dependencies = package_json.get("dependencies", {})
        dev_dependencies = package_json.get("devDependencies", {})
        all_deps = {**dependencies, **dev_dependencies}
        if "react" in all_deps:
            add_framework_signal(framework_signals, "React", 0.95)
        if "next" in all_deps:
            add_framework_signal(framework_signals, "Next.js", 0.95)
        if "vue" in all_deps:
            add_framework_signal(framework_signals, "Vue", 0.9)
        if "svelte" in all_deps:
            add_framework_signal(framework_signals, "Svelte", 0.9)
        if "angular" in all_deps:
            add_framework_signal(framework_signals, "Angular", 0.9)
        if "express" in all_deps:
            add_framework_signal(framework_signals, "Express", 0.8)
        if "nestjs" in all_deps:
            add_framework_signal(framework_signals, "NestJS", 0.9)
        if "fastify" in all_deps:
            add_framework_signal(framework_signals, "Fastify", 0.8)
        return

    if filename_lower in {"requirements.txt", "pyproject.toml", "poetry.lock"}:
        text = content.lower()
        if "fastapi" in text:
            add_framework_signal(framework_signals, "FastAPI", 0.9)
        if "django" in text:
            add_framework_signal(framework_signals, "Django", 0.9)
        if "flask" in text:
            add_framework_signal(framework_signals, "Flask", 0.85)
        return

    if filename_lower in {"pom.xml", "build.gradle", "build.gradle.kts"}:
        text = content.lower()
        if "spring" in text:
            add_framework_signal(framework_signals, "Spring", 0.8)
        return

    if filename_lower == "go.mod":
        text = content.lower()
        if "gin-gonic" in text:
            add_framework_signal(framework_signals, "Gin", 0.8)
        if "labstack/echo" in text:
            add_framework_signal(framework_signals, "Echo", 0.8)
        return

    if filename_lower == "cargo.toml":
        text = content.lower()
        if "rocket" in text:
            add_framework_signal(framework_signals, "Rocket", 0.8)
        if "actix" in text:
            add_framework_signal(framework_signals, "Actix", 0.8)
        return

    if filename_lower in {"next.config.js", "nuxt.config.js", "vite.config.js"}:
        if filename_lower == "next.config.js":
            add_framework_signal(framework_signals, "Next.js", 0.9)
        if filename_lower == "nuxt.config.js":
            add_framework_signal(framework_signals, "Nuxt", 0.9)
        if filename_lower == "vite.config.js":
            add_framework_signal(framework_signals, "Vite", 0.8)
        return

    extension = file_path.suffix.lower()
    if extension in {".jsx", ".tsx"}:
        add_framework_signal(framework_signals, "React", 0.6)
    if extension == ".py":
        text = content.lower()
        if "fastapi" in text:
            add_framework_signal(framework_signals, "FastAPI", 0.7)


def add_framework_signal(
    framework_signals: dict[str, FrameworkSignal],
    name: str,
    confidence: float,
) -> None:
    current = framework_signals.get(name)
    if current and current.confidence >= confidence:
        return
    framework_signals[name] = FrameworkSignal(name=name, confidence=confidence)


def detect_databases(
    content: str,
    extension: str,
    rel_path: str,
    database_signal_map: dict[str, set[str]],
) -> None:
    if extension not in ALLOWED_DB_SIGNAL_EXTENSIONS:
        return
    text = content.lower()
    for keyword, db_name in DATABASE_KEYWORDS.items():
        if keyword in text:
            database_signal_map[db_name].add(rel_path)
