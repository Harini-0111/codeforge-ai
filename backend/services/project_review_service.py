from models.project import ProjectMap
from services.llm_service import review_project_map


def generate_project_review(project_map: ProjectMap) -> str:
    if hasattr(project_map, "model_dump"):
        payload = project_map.model_dump()
    else:
        payload = project_map.dict()
    return review_project_map(payload)
