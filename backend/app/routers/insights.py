"""Insights router: evening productivity digest."""

import logging
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.exceptions import raise_openai_http
from app.services.digest import get_digest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/digest", response_model=schemas.DigestResponse)
def get_evening_digest(
    target_date: date | None = Query(default=None, alias="date"),
    refresh: bool = False,
    db: Session = Depends(get_db),
) -> schemas.DigestResponse:
    """Return an AI evening digest for the given date.

    Results are cached in memory for the calendar day unless
    ``refresh`` is true.

    Args:
        target_date: Date to summarize (defaults to today)
        refresh: Bypass the daily cache
        db: Database session

    Returns:
        Digest text and aggregated stats

    Raises:
        HTTPException: If OpenAI generation fails
    """
    logger.info(
        "Digest requested date=%s refresh=%s",
        target_date,
        refresh,
    )
    try:
        payload = get_digest(
            db,
            target=target_date,
            refresh=refresh,
        )
    except Exception as exc:
        logger.error("Digest generation failed: %s", str(exc))
        raise_openai_http(
            exc,
            fallback="Не удалось сформировать дайджест.",
        )

    return schemas.DigestResponse.model_validate(payload)
