from sqlalchemy.orm import Session

from models.review import Review, ReviewResponse
from services.llm_service import MODEL_NAME, review_code

DEFAULT_LANGUAGE = "unknown"


def save_review(
    db: Session,
    code: str,
    review_text: str,
    language: str,
    model: str,
) -> Review:
    """Persist a review record and return the ORM object."""
    record = Review(
        code=code,
        review=review_text,
        language=language,
        model=model,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def to_review_response(record: Review) -> ReviewResponse:
    """Convert an ORM record to a response DTO."""
    return ReviewResponse(
        id=record.id,
        code=record.code,
        review=record.review,
        language=record.language,
        model=record.model,
        created_at=record.created_at,
    )


def create_review(db: Session, code: str, language: str | None = None) -> ReviewResponse:
    """Generate, store, and return a review."""
    review_text = review_code(code)
    normalized_language = language or DEFAULT_LANGUAGE
    record = save_review(
        db=db,
        code=code,
        review_text=review_text,
        language=normalized_language,
        model=MODEL_NAME,
    )
    return to_review_response(record)


def get_reviews(db: Session, limit: int = 10) -> list[ReviewResponse]:
    """Fetch recent reviews, newest first."""
    records = (
        db.query(Review)
        .order_by(Review.created_at.desc())
        .limit(limit)
        .all()
    )
    return [to_review_response(record) for record in records]


def get_review_by_id(db: Session, review_id: int) -> ReviewResponse | None:
    """Fetch a single review by ID."""
    record = db.query(Review).filter(Review.id == review_id).first()
    if not record:
        return None
    return to_review_response(record)
