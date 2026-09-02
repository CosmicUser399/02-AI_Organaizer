"""SQLAlchemy database models."""

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Task(Base):
    """Task model."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    raw_input = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    due_at = Column(DateTime, nullable=True)
    tag = Column(String(50), nullable=True)
    is_urgent = Column(Boolean, default=False)
    is_important = Column(Boolean, default=False)
    status = Column(String(20), default="pending")  # pending/in_progress/done
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    checklist_items = relationship(
        "ChecklistItem", back_populates="task", cascade="all, delete-orphan"
    )
    notes = relationship("Note", back_populates="linked_task")


class ChecklistItem(Base):
    """Checklist item model for task decomposition."""

    __tablename__ = "checklist_items"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    text = Column(Text, nullable=False)
    is_done = Column(Boolean, default=False)
    position = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="checklist_items")


class Note(Base):
    """Note model with AI capabilities."""

    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(JSON, default=list)  # List of tags
    linked_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    linked_task = relationship("Task", back_populates="notes")
    chunks = relationship(
        "NoteChunk", back_populates="note", cascade="all, delete-orphan"
    )


class NoteChunk(Base):
    """Note chunk with embedding for semantic search."""

    __tablename__ = "note_chunks"

    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=False)
    text = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True)  # List of floats

    note = relationship("Note", back_populates="chunks")
