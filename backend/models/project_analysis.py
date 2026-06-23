from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from database import Base


class ProjectAnalysis(Base):
    __tablename__ = "project_analyses"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(255), nullable=False)
    project_path = Column(String(512), nullable=False)
    source_type = Column(String(50), nullable=True)
    source_locator = Column(String(1024), nullable=True)
    source_ref = Column(String(255), nullable=True)
    source_commit = Column(String(64), nullable=True)
    repository_metadata = Column(Text, nullable=True)
    project_map = Column(Text, nullable=False)
    review = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
