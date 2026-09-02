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
    completed_at: Optional[datetime] = None
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


class ChecklistItemUpdate(BaseModel):
    """Schema for updating a checklist item."""

    text: Optional[str] = None
    is_done: Optional[bool] = None
    position: Optional[int] = None


class DecomposeResponse(BaseModel):
    """Schema for task decomposition response."""

    checklist_items: list[ChecklistItemResponse]
    suggestions: list[str]


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


class NotesAskRequest(BaseModel):
    """Schema for semantic search over notes."""

    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


class NotesAskMatch(BaseModel):
    """One semantically similar note fragment."""

    note_id: int
    note_title: str
    chunk_text: str
    score: float


class NotesAskResponse(BaseModel):
    """Schema for semantic search response."""

    question: str
    answer: str
    matches: list[NotesAskMatch]


class NoteTransformRequest(BaseModel):
    """Schema for quick formatting of selected note text."""

    selection: str = Field(..., min_length=1)
    mode: str = Field(
        ...,
        pattern=("^(summarize|fix_grammar|tone_business|tone_friendly)$"),
    )


class NoteTransformResponse(BaseModel):
    """Schema for transformed note text."""

    result: str
    mode: str


class ScheduleTaskItem(BaseModel):
    """Task with planner metadata."""

    id: int
    title: str
    due_at: Optional[datetime] = None
    tag: Optional[str] = None
    is_urgent: bool
    is_important: bool
    status: str
    priority_score: float
    quadrant: str
    is_overdue: bool


class ScheduleQuadrants(BaseModel):
    """Eisenhower matrix buckets."""

    do_first: list[ScheduleTaskItem]
    schedule: list[ScheduleTaskItem]
    delegate: list[ScheduleTaskItem]
    later: list[ScheduleTaskItem]


class ScheduleTodayResponse(BaseModel):
    """Today's focus list and priority quadrants."""

    date: str
    focus_tasks: list[ScheduleTaskItem]
    quadrants: ScheduleQuadrants
    overdue: list[ScheduleTaskItem]


class RescheduleResponse(BaseModel):
    """Suggested new window for an overdue task."""

    task_id: int
    current_due_at: Optional[datetime] = None
    suggested_due_at: datetime
    reason: str
    day_load_summary: str


class TaskProgressItem(BaseModel):
    """Task with partial checklist progress."""

    title: str
    progress: str
    percent: int


class DigestStats(BaseModel):
    """Aggregated productivity numbers for a day."""

    date: str
    total_open_and_done_today: int
    completed_count: int
    completion_percent: float
    most_productive_period: Optional[str] = None
    completed_titles: list[str]
    tomorrow_hard_tasks: list[str]
    overdue_titles: list[str]
    in_progress_tasks: list[TaskProgressItem]


class DigestResponse(BaseModel):
    """Evening AI digest payload."""

    date: str
    text: str
    stats: DigestStats
    cached: bool
