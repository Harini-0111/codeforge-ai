from datetime import datetime

from pydantic import BaseModel


class FrameworkSignal(BaseModel):
    name: str
    confidence: float


class DatabaseSignal(BaseModel):
    name: str
    evidence: list[str]


class DirectorySummary(BaseModel):
    path: str
    file_count: int


class FileClassification(BaseModel):
    path: str
    category: str


class ProjectMap(BaseModel):
    project_name: str
    languages: list[str]
    frameworks: list[str]
    framework_confidence: list[FrameworkSignal]
    package_managers: list[str]
    file_counts: dict[str, int]
    important_files: list[str]
    entry_points: list[str]
    directory_summary: list[DirectorySummary]
    database_signals: list[DatabaseSignal]
    file_classifications: list[FileClassification]


class ProjectScanRequest(BaseModel):
    root_path: str


class ProjectScanResponse(BaseModel):
    project_map: ProjectMap
    review: str


class ProjectAnalysisSummary(BaseModel):
    id: int
    project_name: str
    project_path: str
    created_at: datetime


class ProjectAnalysisResponse(BaseModel):
    id: int
    project_name: str
    project_path: str
    project_map: ProjectMap
    review: str
    created_at: datetime
