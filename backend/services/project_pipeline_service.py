from sqlalchemy.orm import Session

from models.project import ProjectScanResponse
from services.project_analysis_service import save_project_analysis
from services.project_review_service import generate_project_review
from services.project_scan_service import scan_project
from services.source_adapter_service import PreparedProjectSource


def analyze_project(
    db: Session,
    source: PreparedProjectSource,
) -> ProjectScanResponse:
    project_map = scan_project(str(source.project_root))
    review = generate_project_review(project_map)
    save_project_analysis(
        db=db,
        project_path=str(source.project_root),
        project_map=project_map,
        review=review,
        source_metadata=source.metadata,
    )
    return ProjectScanResponse(project_map=project_map, review=review)
