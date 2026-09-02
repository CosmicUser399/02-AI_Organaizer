"""Database configuration and session management."""

import logging

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # SQLite specific
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def ensure_schema() -> None:
    """Add columns that create_all will not alter on existing DBs."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    if "tasks" not in tables:
        return
    columns = {col["name"] for col in inspector.get_columns("tasks")}
    if "completed_at" not in columns:
        logger.info("Adding tasks.completed_at column")
        with engine.begin() as conn:
            conn.execute(
                text("ALTER TABLE tasks " "ADD COLUMN completed_at DATETIME")
            )


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
