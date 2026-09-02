"""Schedule router: daily focus and Eisenhower matrix."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.services.scheduler import build_today_schedule

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/schedule", tags=["schedule"])


@router.get("/today", response_model=schemas.ScheduleTodayResponse)
def get_today_schedule(
    db: Session = Depends(get_db),
) -> schemas.ScheduleTodayResponse:
    """Return today's focus tasks grouped by Eisenhower quadrant.

    Args:
        db: Database session

    Returns:
        Focus list, quadrants, and overdue tasks
    """
    logger.info("Building today's schedule")
    payload = build_today_schedule(db)
    return schemas.ScheduleTodayResponse.model_validate(payload)
