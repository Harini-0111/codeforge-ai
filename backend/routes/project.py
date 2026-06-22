from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from database import get_db
from models.project import (
    ProjectAnalysisResponse,
    ProjectAnalysisSummary,
    GitHubProjectRequest,
    ProjectScanRequest,
    ProjectScanResponse,
)
from services.project_analysis_service import get_project_analysis, get_project_analyses
from services.project_pipeline_service import analyze_project
from services.source_adapter_service import (
    prepare_github_source,
    prepare_local_source,
    prepare_zip_source,
)

router = APIRouter()


@router.post("/api/projects/scan", response_model=ProjectScanResponse)
def scan_project_folder(
    request: ProjectScanRequest,
    db: Session = Depends(get_db),
) -> ProjectScanResponse:
    """Scan a local project folder and return a project map + review."""
    try:
        source = prepare_local_source(request.root_path)
        return analyze_project(db, source)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/projects", response_model=list[ProjectAnalysisSummary])
def list_project_analyses(
    db: Session = Depends(get_db),
) -> list[ProjectAnalysisSummary]:
    """Return recent project analyses."""
    return get_project_analyses(db, limit=10)


@router.get("/api/projects/{analysis_id}", response_model=ProjectAnalysisResponse)
def fetch_project_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
) -> ProjectAnalysisResponse:
    """Return a saved project analysis by ID."""
    analysis = get_project_analysis(db, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Project analysis not found")
    return analysis


@router.post("/api/projects/upload", response_model=ProjectScanResponse)
def upload_project_zip(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ProjectScanResponse:
    """Upload a zip file, extract safely, and run project analysis."""
    try:
        source = prepare_zip_source(file)
        return analyze_project(db, source)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/api/projects/github", response_model=ProjectScanResponse)
def analyze_github_repository(
    request: GitHubProjectRequest,
    db: Session = Depends(get_db),
) -> ProjectScanResponse:
    """Download and analyze a public GitHub repository."""
    try:
        source = prepare_github_source(request.repository_url, request.ref)
        return analyze_project(db, source)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
