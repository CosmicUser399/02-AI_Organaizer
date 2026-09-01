"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# Task schemas
class TaskBase(BaseModel):
    """Base task schema."""

    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    tag: Optional[str] = Field(None, max_length=50)
    is_urgent: bool = False
    is_important: bool = False


class TaskCreate(TaskBase):
    """Schema for creating a task."""

    raw_input: Optional[str] = None


class TaskUpdate(BaseModel):
    """Schema for updating a task."""

    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    tag: Optional[str] = Field(None, max_length=50)
    is_urgent: Optional[bool] = None
    is_important: Optional[bool] = None
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|done)$")


class TaskResponse(TaskBase):
    """Schema for task response."""

    id: int
    raw_input: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ChecklistItem schemas
class ChecklistItemBase(BaseModel):
    """Base checklist item schema."""

    text: str
    position: int = 0


class ChecklistItemCreate(ChecklistItemBase):
    """Schema for creating a checklist item."""

    pass


class ChecklistItemResponse(ChecklistItemBase):
    """Schema for checklist item response."""

    id: int
    task_id: int
    is_done: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Note schemas
class NoteBase(BaseModel):
    """Base note schema."""

    title: str = Field(..., max_length=255)
    content: str
    tags: list[str] = Field(default_factory=list)
    linked_task_id: Optional[int] = None


class NoteCreate(NoteBase):
    """Schema for creating a note."""

    pass


class NoteUpdate(BaseModel):
    """Schema for updating a note."""

    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    tags: Optional[list[str]] = None
    linked_task_id: Optional[int] = None


class NoteResponse(NoteBase):
    """Schema for note response."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
