"""Adaptive scheduler: Eisenhower priorities and reschedule."""

import logging
from datetime import datetime, timedelta

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app import models
from app.services.openai_client import openai_client

logger = logging.getLogger(__name__)

QUADRANT_DO_FIRST = "do_first"
QUADRANT_SCHEDULE = "schedule"
QUADRANT_DELEGATE = "delegate"
QUADRANT_LATER = "later"

_QUADRANT_BASE = {
    (True, True): 100.0,
    (False, True): 70.0,
    (True, False): 40.0,
    (False, False): 10.0,
}


class RescheduleProposal(BaseModel):
    """Structured output for a smart reschedule suggestion."""

    suggested_due_at: datetime = Field(
        ...,
        description="Proposed new due datetime in ISO format",
    )
    reason: str = Field(
        ...,
        description="Short explanation of why this slot fits",
    )
    day_load_summary: str = Field(
        ...,
        description="Brief summary of remaining day load",
    )


def as_naive(dt: datetime | None) -> datetime | None:
    """Strip timezone info for SQLite-naive comparisons.

    Args:
        dt: Datetime that may be aware or naive

    Returns:
        Naive datetime or None
    """
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


def now_naive() -> datetime:
    """Return current local time as a naive datetime."""
    return datetime.now().replace(tzinfo=None)


def quadrant_for(task: models.Task) -> str:
    """Return Eisenhower quadrant key for a task."""
    urgent = bool(task.is_urgent)
    important = bool(task.is_important)
    if urgent and important:
        return QUADRANT_DO_FIRST
    if important:
        return QUADRANT_SCHEDULE
    if urgent:
        return QUADRANT_DELEGATE
    return QUADRANT_LATER


def _due_boost(due_at: datetime | None, now: datetime) -> float:
    """Extra score from deadline proximity and overdue status."""
    due = as_naive(due_at)
    if due is None:
        return 0.0
    if due < now:
        hours_overdue = (now - due).total_seconds() / 3600
        return 30.0 + min(hours_overdue, 48.0) * 0.25
    hours_left = (due - now).total_seconds() / 3600
    if hours_left <= 24:
        return 20.0
    if hours_left <= 72:
        return 10.0
    return 0.0


def priority_score(task: models.Task, now: datetime | None = None) -> float:
    """Compute a sortable priority score for a task.

    Args:
        task: Task to score
        now: Reference time (defaults to local now)

    Returns:
        Higher score means higher focus priority
    """
    moment = now if now is not None else now_naive()
    base = _QUADRANT_BASE[(bool(task.is_urgent), bool(task.is_important))]
    return base + _due_boost(task.due_at, moment)


def is_overdue(task: models.Task, now: datetime | None = None) -> bool:
    """Return True if the task has a due date in the past."""
    moment = now if now is not None else now_naive()
    due = as_naive(task.due_at)
    if due is None or task.status == "done":
        return False
    return due < moment


def _to_item(task: models.Task, now: datetime) -> dict:
    """Serialize a task with scheduler metadata."""
    return {
        "id": task.id,
        "title": task.title,
        "due_at": task.due_at,
        "tag": task.tag,
        "is_urgent": bool(task.is_urgent),
        "is_important": bool(task.is_important),
        "status": task.status,
        "priority_score": round(priority_score(task, now), 2),
        "quadrant": quadrant_for(task),
        "is_overdue": is_overdue(task, now),
    }


def build_today_schedule(db: Session) -> dict:
    """Build today's focus list and Eisenhower quadrants.

    Args:
        db: Database session

    Returns:
        Schedule payload with focus, quadrants, and overdue
    """
    now = now_naive()
    tasks = db.query(models.Task).filter(models.Task.status != "done").all()
    items = [_to_item(task, now) for task in tasks]
    items.sort(key=lambda item: item["priority_score"], reverse=True)

    quadrants = {
        QUADRANT_DO_FIRST: [],
        QUADRANT_SCHEDULE: [],
        QUADRANT_DELEGATE: [],
        QUADRANT_LATER: [],
    }
    overdue = []
    for item in items:
        quadrants[item["quadrant"]].append(item)
        if item["is_overdue"]:
            overdue.append(item)

    today_end = now.replace(hour=23, minute=59, second=59, microsecond=0)
    due_today = []
    for item in items:
        due = as_naive(item["due_at"])
        if due is not None and due.date() == now.date() and due <= today_end:
            due_today.append(item)

    focus: list[dict] = []
    seen: set[int] = set()
    for item in overdue + due_today + quadrants[QUADRANT_DO_FIRST]:
        if item["id"] in seen:
            continue
        focus.append(item)
        seen.add(item["id"])
        if len(focus) >= 3:
            break
    if len(focus) < 3:
        for item in items:
            if item["id"] in seen:
                continue
            focus.append(item)
            seen.add(item["id"])
            if len(focus) >= 3:
                break

    logger.info(
        "Built schedule for %s: %d open tasks, %d overdue",
        now.date().isoformat(),
        len(items),
        len(overdue),
    )
    return {
        "date": now.date().isoformat(),
        "focus_tasks": focus,
        "quadrants": quadrants,
        "overdue": overdue,
    }


def _day_load_lines(db: Session, now: datetime) -> str:
    """Describe remaining scheduled work for the next two days."""
    horizon = now + timedelta(days=2)
    tasks = db.query(models.Task).filter(models.Task.status != "done").all()
    lines: list[str] = []
    for task in tasks:
        due = as_naive(task.due_at)
        if due is None:
            continue
        if due < now or due > horizon:
            continue
        lines.append(
            f"- {task.title} (due {due.isoformat(timespec='minutes')}, "
            f"urgent={bool(task.is_urgent)}, "
            f"important={bool(task.is_important)})"
        )
    if not lines:
        return "No other timed tasks in the next two days."
    return "\n".join(lines)


def propose_reschedule(
    db: Session,
    task: models.Task,
) -> RescheduleProposal:
    """Propose a new time window for an overdue task.

    Args:
        db: Database session
        task: Overdue task to reschedule

    Returns:
        Validated reschedule proposal

    Raises:
        ValueError: If the task is not overdue
        Exception: If OpenAI API call fails
    """
    now = now_naive()
    if not is_overdue(task, now):
        raise ValueError("Task is not overdue")

    load = _day_load_lines(db, now)
    due = as_naive(task.due_at)
    system_message = (
        "You are a scheduling assistant. Suggest a realistic new "
        "due datetime for an overdue task. Prefer a free slot later "
        "today; if the day is packed, use tomorrow morning. Avoid "
        "colliding with existing due times. Keep reason short."
    )
    prompt = (
        f"Current datetime: {now.isoformat(timespec='minutes')}\n"
        f"Overdue task: {task.title}\n"
        f"Original due_at: {due.isoformat() if due else 'unknown'}\n"
        f"Urgent: {bool(task.is_urgent)}\n"
        f"Important: {bool(task.is_important)}\n"
        f"Description: {task.description or '-'}\n\n"
        f"Existing load:\n{load}"
    )
    logger.info("Requesting reschedule proposal for task id=%d", task.id)
    proposal = openai_client.structured_completion(
        prompt=prompt,
        response_format=RescheduleProposal,
        system_message=system_message,
        temperature=0.3,
    )
    proposal.suggested_due_at = as_naive(proposal.suggested_due_at)
    if proposal.suggested_due_at is None:
        proposal.suggested_due_at = now + timedelta(hours=2)
    if proposal.suggested_due_at < now:
        proposal.suggested_due_at = now + timedelta(hours=2)
    logger.info(
        "Reschedule proposed for task id=%d at %s",
        task.id,
        proposal.suggested_due_at.isoformat(),
    )
    return proposal
