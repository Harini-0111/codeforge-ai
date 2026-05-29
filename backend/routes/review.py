from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.review import CodeReviewRequest, ReviewResponse
from services.review_service import create_review, get_review_by_id, get_reviews

router = APIRouter()

@router.get("/")
def home():
    return {"message": "CodeForge AI Backend Running"}

@router.post("/api/review", response_model=ReviewResponse)
def review_code(
    request: CodeReviewRequest,
    db: Session = Depends(get_db),
) -> ReviewResponse:
    """Generate and store a review."""
    return create_review(db, request.code, request.language)


@router.get("/api/reviews", response_model=list[ReviewResponse])
def list_reviews(db: Session = Depends(get_db)) -> list[ReviewResponse]:
    """Return recent reviews."""
    return get_reviews(db, limit=10)


@router.get("/api/reviews/{review_id}", response_model=ReviewResponse)
def fetch_review(
    review_id: int,
    db: Session = Depends(get_db),
) -> ReviewResponse:
    """Return a single review by ID."""
    review = get_review_by_id(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review
