from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.project import (
    ProjectAnalysisResponse,
    ProjectAnalysisSummary,
    ProjectScanRequest,
    ProjectScanResponse,
)
from services.project_analysis_service import (
    get_project_analysis,
    get_project_analyses,
    save_project_analysis,
)
from services.project_review_service import generate_project_review
from services.project_scan_service import scan_project

router = APIRouter()


@router.post("/api/projects/scan", response_model=ProjectScanResponse)
def scan_project_folder(
    request: ProjectScanRequest,
    db: Session = Depends(get_db),
) -> ProjectScanResponse:
    """Scan a local project folder and return a project map + review."""
    try:
        project_map = scan_project(request.root_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    review = generate_project_review(project_map)
    save_project_analysis(db, request.root_path, project_map, review)
    return ProjectScanResponse(project_map=project_map, review=review)


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
