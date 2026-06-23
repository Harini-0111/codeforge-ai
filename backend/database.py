from sqlalchemy import create_engine, inspect, text
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
    from models import project_analysis, review  # noqa: F401
    Base.metadata.create_all(bind=engine)
    ensure_project_analysis_source_columns()


def ensure_project_analysis_source_columns() -> None:
    """Keep existing SQLite databases compatible without a migration framework."""
    inspector = inspect(engine)
    if "project_analyses" not in inspector.get_table_names():
        return

    existing_columns = {
        column["name"] for column in inspector.get_columns("project_analyses")
    }
    source_columns = {
        "source_type": "VARCHAR(50)",
        "source_locator": "VARCHAR(1024)",
        "source_ref": "VARCHAR(255)",
        "source_commit": "VARCHAR(64)",
        "repository_metadata": "TEXT",
    }

    with engine.begin() as connection:
        for column_name, column_type in source_columns.items():
            if column_name not in existing_columns:
                connection.execute(
                    text(
                        f"ALTER TABLE project_analyses "
                        f"ADD COLUMN {column_name} {column_type}"
                    )
                )
