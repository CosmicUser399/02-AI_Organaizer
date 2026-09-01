"""Tasks router with CRUD operations."""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

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
    logger.info(
        "Fetching tasks with skip=%d, limit=%d", skip, limit
    )
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
    db_task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()
    if db_task is None:
        logger.warning("Task with id=%d not found", task_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    update_data = task_update.model_dump(exclude_unset=True)
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
    db_task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()
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
