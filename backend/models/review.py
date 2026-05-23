from pydantic import BaseModel
from typing import List

class CodeReviewRequest(BaseModel):
    code: str

class CodeReviewResponse(BaseModel):
    issues: List[str]
    score: int
    suggestions: List[str]
