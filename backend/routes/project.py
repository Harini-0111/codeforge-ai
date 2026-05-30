from fastapi import APIRouter, HTTPException

from models.project import ProjectScanRequest, ProjectScanResponse
from services.project_review_service import generate_project_review
from services.project_scan_service import scan_project

router = APIRouter()


@router.post("/api/projects/scan", response_model=ProjectScanResponse)
def scan_project_folder(request: ProjectScanRequest) -> ProjectScanResponse:
    """Scan a local project folder and return a project map + review."""
    try:
        project_map = scan_project(request.root_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    review = generate_project_review(project_map)
    return ProjectScanResponse(project_map=project_map, review=review)
