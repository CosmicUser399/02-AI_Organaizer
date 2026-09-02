"""Tasks router with CRUD operations."""

import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.exceptions import raise_openai_http
from app.services.capture import parse_magic_input
from app.services.decompose import decompose_task
from app.services.scheduler import propose_reschedule

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=List[schemas.TaskResponse])
def get_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[models.Task]:
    """
    Get all tasks with optional pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List of tasks
    """
    logger.info("Fetching tasks with skip=%d, limit=%d", skip, limit)
    tasks = db.query(models.Task).offset(skip).limit(limit).all()
    return tasks


@router.get("/{task_id}", response_model=schemas.TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
) -> models.Task:
    """
    Get a specific task by ID.

    Args:
        task_id: Task ID
        db: Database session

    Returns:
        Task object

    Raises:
        HTTPException: If task not found
    """
    logger.info("Fetching task with id=%d", task_id)
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task is None:
        logger.warning("Task with id=%d not found", task_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return task


@router.post(
    "/",
    response_model=schemas.TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
) -> models.Task:
    """
    Create a new task.

    Args:
        task: Task creation schema
        db: Database session

    Returns:
        Created task object
    """
    logger.info("Creating new task: %s", task.title)
    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    logger.info("Task created successfully with id=%d", db_task.id)
    return db_task


@router.patch("/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db),
) -> models.Task:
    """
    Update an existing task.

    Args:
        task_id: Task ID
        task_update: Task update schema with partial data
        db: Database session

    Returns:
        Updated task object

    Raises:
        HTTPException: If task not found
    """
    logger.info("Updating task with id=%d", task_id)
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        logger.warning("Task with id=%d not found", task_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    update_data = task_update.model_dump(exclude_unset=True)
    if "status" in update_data:
        new_status = update_data["status"]
        if new_status == "done" and db_task.status != "done":
            db_task.completed_at = datetime.utcnow()
        elif new_status != "done":
            db_task.completed_at = None

    for field, value in update_data.items():
        setattr(db_task, field, value)

    db.commit()
    db.refresh(db_task)
    logger.info("Task with id=%d updated successfully", task_id)
    return db_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a specific task.

    Args:
        task_id: Task ID
        db: Database session

    Raises:
        HTTPException: If task not found
    """
    logger.info("Deleting task with id=%d", task_id)
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        logger.warning("Task with id=%d not found", task_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    db.delete(db_task)
    db.commit()
    logger.info("Task with id=%d deleted successfully", task_id)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_all_tasks(
    db: Session = Depends(get_db),
) -> None:
    """
    Delete all tasks (clear the task list).

    Args:
        db: Database session
    """
    logger.info("Deleting all tasks")
    deleted_count = db.query(models.Task).delete()
    db.commit()
    logger.info("Deleted %d tasks", deleted_count)


class MagicInputRequest(BaseModel):
    """Request schema for magic input parsing."""

    raw_input: str


@router.post(
    "/parse",
    response_model=schemas.TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def parse_and_create_task(
    request: MagicInputRequest,
    db: Session = Depends(get_db),
) -> models.Task:
    """
    Parse natural language input and create task.

    Uses AI to extract structured task details from free-form text
    and saves it to the database.

    Args:
        request: Magic input request with raw text
        db: Database session

    Returns:
        Created task object

    Raises:
        HTTPException: If AI parsing fails
    """
    logger.info("Parsing magic input: %s", request.raw_input[:50])

    try:
        parsed = parse_magic_input(request.raw_input)
    except Exception as e:
        logger.error("Failed to parse magic input: %s", str(e))
        raise_openai_http(
            e,
            fallback="Не удалось разобрать запрос. Попробуйте ещё раз.",
        )

    # Create task with parsed data
    task_data = {
        "title": parsed.title,
        "description": parsed.description,
        "due_at": parsed.due_at,
        "tag": parsed.tag,
        "is_urgent": parsed.is_urgent,
        "is_important": parsed.is_important,
        "raw_input": request.raw_input,
        "status": "pending",
    }

    db_task = models.Task(**task_data)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    logger.info("Task created from magic input with id=%d", db_task.id)
    return db_task


@router.post(
    "/{task_id}/decompose",
    response_model=schemas.DecomposeResponse,
)
def decompose_task_endpoint(
    task_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """
    Decompose task into checklist items using AI.

    Uses AI to break down a task into actionable steps
    and provides contextual suggestions.

    Args:
        task_id: Task ID to decompose
        db: Database session

    Returns:
        DecomposeResponse with checklist items and suggestions

    Raises:
        HTTPException: If task not found or AI decomposition fails
    """
    logger.info("Decomposing task with id=%d", task_id)

    # Get task
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        logger.warning("Task with id=%d not found", task_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    # Decompose using AI
    try:
        decomposed = decompose_task(
            title=db_task.title,
            description=db_task.description,
        )
    except Exception as e:
        logger.error("Failed to decompose task: %s", str(e))
        raise_openai_http(
            e,
            fallback="Не удалось разбить задачу на шаги.",
        )

    # Create checklist items
    created_items = []
    for position, text in enumerate(decomposed.checklist_items):
        item = models.ChecklistItem(
            task_id=task_id,
            text=text,
            position=position,
        )
        db.add(item)
        created_items.append(item)

    db.commit()
    for item in created_items:
        db.refresh(item)

    logger.info(
        "Task decomposed: created %d checklist items", len(created_items)
    )

    return {
        "checklist_items": created_items,
        "suggestions": decomposed.suggestions,
    }


@router.get(
    "/{task_id}/checklist",
    response_model=List[schemas.ChecklistItemResponse],
)
def get_checklist(
    task_id: int,
    db: Session = Depends(get_db),
) -> List[models.ChecklistItem]:
    """
    Get all checklist items for a task.

    Args:
        task_id: Task ID
        db: Database session

    Returns:
        List of checklist items ordered by position

    Raises:
        HTTPException: If task not found
    """
    logger.info("Fetching checklist for task id=%d", task_id)

    # Check task exists
    task_exists = (
        db.query(models.Task).filter(models.Task.id == task_id).first()
    )
    if task_exists is None:
        logger.warning("Task with id=%d not found", task_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    items = (
        db.query(models.ChecklistItem)
        .filter(models.ChecklistItem.task_id == task_id)
        .order_by(models.ChecklistItem.position)
        .all()
    )
    return items


@router.post(
    "/{task_id}/checklist",
    response_model=schemas.ChecklistItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_checklist_item(
    task_id: int,
    item_create: schemas.ChecklistItemCreate,
    db: Session = Depends(get_db),
) -> models.ChecklistItem:
    """
    Add a new checklist item to a task.

    Args:
        task_id: Task ID
        item_create: New checklist item data
        db: Database session

    Returns:
        Created checklist item

    Raises:
        HTTPException: If task not found
    """
    logger.info("Adding checklist item to task id=%d", task_id)

    task_exists = (
        db.query(models.Task).filter(models.Task.id == task_id).first()
    )
    if task_exists is None:
        logger.warning("Task with id=%d not found", task_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    db_item = models.ChecklistItem(
        task_id=task_id,
        text=item_create.text,
        position=item_create.position,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    logger.info(
        "Checklist item %d added to task %d",
        db_item.id,
        task_id,
    )
    return db_item


@router.patch(
    "/{task_id}/checklist/{item_id}",
    response_model=schemas.ChecklistItemResponse,
)
def update_checklist_item(
    task_id: int,
    item_id: int,
    item_update: schemas.ChecklistItemUpdate,
    db: Session = Depends(get_db),
) -> models.ChecklistItem:
    """
    Update a checklist item.

    Args:
        task_id: Task ID
        item_id: Checklist item ID
        item_update: Update data
        db: Database session

    Returns:
        Updated checklist item

    Raises:
        HTTPException: If task or item not found
    """
    logger.info("Updating checklist item %d for task %d", item_id, task_id)

    db_item = (
        db.query(models.ChecklistItem)
        .filter(
            models.ChecklistItem.id == item_id,
            models.ChecklistItem.task_id == task_id,
        )
        .first()
    )

    if db_item is None:
        logger.warning("Checklist item %d not found", item_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Checklist item with id {item_id} not found",
        )

    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)

    db.commit()
    db.refresh(db_item)

    logger.info("Checklist item %d updated successfully", item_id)
    return db_item


@router.delete(
    "/{task_id}/checklist/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_checklist_item(
    task_id: int,
    item_id: int,
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a checklist item.

    Args:
        task_id: Task ID
        item_id: Checklist item ID
        db: Database session

    Raises:
        HTTPException: If task or item not found
    """
    logger.info("Deleting checklist item %d for task %d", item_id, task_id)

    db_item = (
        db.query(models.ChecklistItem)
        .filter(
            models.ChecklistItem.id == item_id,
            models.ChecklistItem.task_id == task_id,
        )
        .first()
    )

    if db_item is None:
        logger.warning("Checklist item %d not found", item_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Checklist item with id {item_id} not found",
        )

    db.delete(db_item)
    db.commit()

    logger.info("Checklist item %d deleted successfully", item_id)


@router.post(
    "/{task_id}/reschedule",
    response_model=schemas.RescheduleResponse,
)
def reschedule_task(
    task_id: int,
    db: Session = Depends(get_db),
) -> schemas.RescheduleResponse:
    """Suggest a new time window for an overdue task.

    Does not apply the change; the client confirms via PATCH.

    Args:
        task_id: Task ID
        db: Database session

    Returns:
        Proposed due time and explanation

    Raises:
        HTTPException: If task is missing, not overdue, or AI fails
    """
    logger.info("Rescheduling task id=%d", task_id)
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        logger.warning("Task with id=%d not found", task_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    try:
        proposal = propose_reschedule(db, db_task)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.error("Reschedule failed: %s", str(exc))
        raise_openai_http(
            exc,
            fallback="Не удалось предложить новое время.",
        )

    return schemas.RescheduleResponse(
        task_id=db_task.id,
        current_due_at=db_task.due_at,
        suggested_due_at=proposal.suggested_due_at,
        reason=proposal.reason,
        day_load_summary=proposal.day_load_summary,
    )
