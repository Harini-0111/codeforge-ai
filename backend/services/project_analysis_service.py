import json

from sqlalchemy.orm import Session

from models.project import ProjectAnalysisResponse, ProjectAnalysisSummary, ProjectMap
from models.project_analysis import ProjectAnalysis


def save_project_analysis(
    db: Session,
    project_path: str,
    project_map: ProjectMap,
    review: str,
) -> ProjectAnalysis:
    payload = (
        project_map.model_dump() if hasattr(project_map, "model_dump") else project_map.dict()
    )
    record = ProjectAnalysis(
        project_name=project_map.project_name,
        project_path=project_path,
        project_map=json.dumps(payload, ensure_ascii=True),
        review=review,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def to_project_summary(record: ProjectAnalysis) -> ProjectAnalysisSummary:
    return ProjectAnalysisSummary(
        id=record.id,
        project_name=record.project_name,
        project_path=record.project_path,
        created_at=record.created_at,
    )


def to_project_response(record: ProjectAnalysis) -> ProjectAnalysisResponse:
    project_map_data = json.loads(record.project_map)
    return ProjectAnalysisResponse(
        id=record.id,
        project_name=record.project_name,
        project_path=record.project_path,
        project_map=ProjectMap(**project_map_data),
        review=record.review,
        created_at=record.created_at,
    )


def get_project_analyses(db: Session, limit: int = 10) -> list[ProjectAnalysisSummary]:
    records = (
        db.query(ProjectAnalysis)
        .order_by(ProjectAnalysis.created_at.desc())
        .limit(limit)
        .all()
    )
    return [to_project_summary(record) for record in records]


def get_project_analysis(db: Session, analysis_id: int) -> ProjectAnalysisResponse | None:
    record = db.query(ProjectAnalysis).filter(ProjectAnalysis.id == analysis_id).first()
    if not record:
        return None
    return to_project_response(record)
