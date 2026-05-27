from models.review import CodeReviewResponse
from services.llm_service import review_code


def analyze_code(code: str) -> CodeReviewResponse:
    """Send code to the LLM and return the review response."""
    review_text = review_code(code)
    return CodeReviewResponse(review=review_text)
