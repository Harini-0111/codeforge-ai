from sqlalchemy import create_engine
from typing import Generator

from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./codeforge.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator:
    """Provide a database session for request lifetimes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create database tables if they do not already exist."""
    # Ensure models are imported so SQLAlchemy knows about them.
    from models import review  # noqa: F401
    Base.metadata.create_all(bind=engine)
