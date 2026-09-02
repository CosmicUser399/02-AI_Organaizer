"""Notes router with CRUD and AI operations."""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.services.embeddings import index_note, search_notes
from app.services.notes_ai import (
    analyze_note,
    suggest_task_link,
    transform_text,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/", response_model=List[schemas.NoteResponse])
def get_notes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[models.Note]:
    """
    Get all notes with optional pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List of notes
    """
    logger.info("Fetching notes with skip=%d, limit=%d", skip, limit)
    notes = db.query(models.Note).offset(skip).limit(limit).all()
    return notes


@router.post("/ask", response_model=schemas.NotesAskResponse)
def ask_notes(
    request: schemas.NotesAskRequest,
    db: Session = Depends(get_db),
) -> schemas.NotesAskResponse:
    """Search notes by meaning and return matching fragments.

    Args:
        request: Question and optional result limit
        db: Database session

    Returns:
        Generated answer plus ranked fragments

    Raises:
        HTTPException: If OpenAI embeddings/search fail
    """
    logger.info("Semantic search: %s", request.question[:80])
    try:
        matches, answer = search_notes(
            db,
            request.question,
            top_k=request.top_k,
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.error("Semantic search failed: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Не удалось выполнить поиск по заметкам",
        ) from exc

    return schemas.NotesAskResponse(
        question=request.question,
        answer=answer,
        matches=[schemas.NotesAskMatch(**item) for item in matches],
    )


@router.get("/{note_id}", response_model=schemas.NoteResponse)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
) -> models.Note:
    """
    Get a specific note by ID.

    Args:
        note_id: Note ID
        db: Database session

    Returns:
        Note object

    Raises:
        HTTPException: If note not found
    """
    logger.info("Fetching note with id=%d", note_id)
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if note is None:
        logger.warning("Note with id=%d not found", note_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )
    return note


@router.post(
    "/",
    response_model=schemas.NoteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_note(
    note: schemas.NoteCreate,
    db: Session = Depends(get_db),
) -> models.Note:
    """
    Create a new note with AI auto-tagging.

    Analyzes note content to automatically extract
    relevant tags if not provided.

    Args:
        note: Note creation schema
        db: Database session

    Returns:
        Created note object
    """
    logger.info("Creating new note: %s", note.title)

    note_data = note.model_dump()

    if not note_data.get("tags"):
        try:
            analysis = analyze_note(note.title, note.content)
            note_data["tags"] = analysis.tags
            logger.info("Auto-generated %d tags for note", len(analysis.tags))
        except Exception as e:
            logger.warning("Failed to auto-tag note: %s", str(e))

    db_note = models.Note(**note_data)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    try:
        index_note(db, db_note)
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.warning(
            "Failed to index new note id=%d: %s",
            db_note.id,
            str(exc),
        )
        db.refresh(db_note)

    logger.info("Note created successfully with id=%d", db_note.id)
    return db_note


@router.patch("/{note_id}", response_model=schemas.NoteResponse)
def update_note(
    note_id: int,
    note_update: schemas.NoteUpdate,
    db: Session = Depends(get_db),
) -> models.Note:
    """
    Update an existing note.

    Re-analyzes content for tags if content changes
    and tags are not explicitly provided.

    Args:
        note_id: Note ID
        note_update: Note update schema with partial data
        db: Database session

    Returns:
        Updated note object

    Raises:
        HTTPException: If note not found
    """
    logger.info("Updating note with id=%d", note_id)

    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if db_note is None:
        logger.warning("Note with id=%d not found", note_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )

    update_data = note_update.model_dump(exclude_unset=True)

    content_changed = "content" in update_data
    tags_provided = "tags" in update_data

    if content_changed and not tags_provided:
        try:
            new_title = update_data.get("title", db_note.title)
            new_content = update_data.get("content", db_note.content)
            analysis = analyze_note(new_title, new_content)
            update_data["tags"] = analysis.tags
            logger.info("Re-generated %d tags for note", len(analysis.tags))
        except Exception as e:
            logger.warning("Failed to auto-tag note: %s", str(e))

    for field, value in update_data.items():
        setattr(db_note, field, value)

    db.commit()
    db.refresh(db_note)

    if content_changed:
        try:
            index_note(db, db_note)
            db.commit()
        except Exception as exc:
            db.rollback()
            logger.warning(
                "Failed to reindex note id=%d: %s",
                note_id,
                str(exc),
            )
            db.refresh(db_note)

    logger.info("Note with id=%d updated successfully", note_id)
    return db_note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a specific note.

    Args:
        note_id: Note ID
        db: Database session

    Raises:
        HTTPException: If note not found
    """
    logger.info("Deleting note with id=%d", note_id)

    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if db_note is None:
        logger.warning("Note with id=%d not found", note_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )

    db.delete(db_note)
    db.commit()
    logger.info("Note with id=%d deleted successfully", note_id)


@router.get("/{note_id}/suggested-tasks")
def get_suggested_task_links(
    note_id: int,
    db: Session = Depends(get_db),
) -> List[dict]:
    """
    Get suggested task links for a note.

    Finds tasks that might be relevant to link with this note
    based on content similarity.

    Args:
        note_id: Note ID
        db: Database session

    Returns:
        List of suggested tasks with relevance scores

    Raises:
        HTTPException: If note not found
    """
    logger.info("Finding suggested tasks for note id=%d", note_id)

    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if db_note is None:
        logger.warning("Note with id=%d not found", note_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )

    tasks = db.query(models.Task).filter(models.Task.status != "done").all()

    suggestions = []
    for task in tasks:
        relevance = suggest_task_link(
            note_title=db_note.title,
            note_content=db_note.content,
            task_title=task.title,
            task_description=task.description,
        )

        if relevance > 0.2:
            suggestions.append(
                {
                    "task_id": task.id,
                    "task_title": task.title,
                    "relevance": round(relevance, 2),
                }
            )

    suggestions.sort(key=lambda x: x["relevance"], reverse=True)
    suggestions = suggestions[:5]

    logger.info("Found %d suggested tasks for note", len(suggestions))
    return suggestions


@router.post(
    "/{note_id}/transform",
    response_model=schemas.NoteTransformResponse,
)
def transform_note_selection(
    note_id: int,
    request: schemas.NoteTransformRequest,
    db: Session = Depends(get_db),
) -> schemas.NoteTransformResponse:
    """Rewrite selected note text (summary, grammar, or tone).

    Args:
        note_id: Note ID (must exist)
        request: Selected fragment and transform mode
        db: Database session

    Returns:
        Transformed text; the note is not saved automatically

    Raises:
        HTTPException: If note is missing or OpenAI fails
    """
    logger.info(
        "Transforming selection for note id=%d mode=%s",
        note_id,
        request.mode,
    )
    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if db_note is None:
        logger.warning("Note with id=%d not found", note_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )

    try:
        result = transform_text(request.selection, request.mode)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.error("Note transform failed: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Не удалось преобразовать текст",
        ) from exc

    return schemas.NoteTransformResponse(
        result=result,
        mode=request.mode,
    )
