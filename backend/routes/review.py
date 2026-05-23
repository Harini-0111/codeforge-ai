from fastapi import APIRouter
from models.review import CodeReviewRequest, CodeReviewResponse
from services.review_service import analyze_code

router = APIRouter()

@router.get("/")
def home():
    return {"message": "CodeForge AI Backend Running"}

@router.post("/api/review", response_model=CodeReviewResponse)
def review_code(request: CodeReviewRequest) -> CodeReviewResponse:
    """
    Endpoint to review code and return analysis.
    """
    review = analyze_code(request.code)
    return review
