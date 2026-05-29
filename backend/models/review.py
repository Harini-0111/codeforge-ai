from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String, Text

from database import Base

class CodeReviewRequest(BaseModel):
    code: str
    language: Optional[str] = None


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(Text, nullable=False)
    review = Column(Text, nullable=False)
    language = Column(String(50), nullable=True)
    model = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ReviewResponse(BaseModel):
    id: int
    code: str
    review: str
    language: str
    model: str
    created_at: datetime
