from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from database import Base


class ProjectAnalysis(Base):
    __tablename__ = "project_analyses"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(255), nullable=False)
    project_path = Column(String(512), nullable=False)
    project_map = Column(Text, nullable=False)
    review = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
