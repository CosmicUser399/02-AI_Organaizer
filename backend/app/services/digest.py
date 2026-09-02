"""Evening AI digest with daily productivity stats."""

import logging
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app import models
from app.services.openai_client import openai_client
from app.services.scheduler import as_naive, now_naive

logger = logging.getLogger(__name__)

_DIGEST_CACHE: dict[str, dict] = {}


def _day_bounds(target: date) -> tuple[datetime, datetime]:
    """Return naive start/end datetimes for a calendar date."""
    start = datetime.combine(target, datetime.min.time())
    end = start + timedelta(days=1)
    return start, end


def _productive_period(hours: list[int]) -> str | None:
    """Map completion hours to a coarse time-of-day label."""
    if not hours:
        return None
    buckets = {
        "утро": 0,
        "день": 0,
        "вечер": 0,
        "ночь": 0,
    }
    for hour in hours:
        if 5 <= hour < 12:
            buckets["утро"] += 1
        elif 12 <= hour < 17:
            buckets["день"] += 1
        elif 17 <= hour < 22:
            buckets["вечер"] += 1
        else:
            buckets["ночь"] += 1
    return max(buckets, key=buckets.get)


def _task_progress(task: models.Task) -> tuple[int, int]:
    """Calculate checklist progress for a task.

    Args:
        task: Task with checklist_items relationship loaded

    Returns:
        Tuple of (completed_items, total_items)
    """
    if not task.checklist_items:
        return (0, 0)
    total = len(task.checklist_items)
    done = sum(1 for item in task.checklist_items if item.is_done)
    return (done, total)


def collect_day_stats(db: Session, target: date) -> dict:
    """Aggregate completion and load statistics for a day.

    Args:
        db: Database session
        target: Calendar date to summarize

    Returns:
        Stats dict used both in the API and the LLM prompt
    """
    start, end = _day_bounds(target)
    all_tasks = db.query(models.Task).all()

    completed_today: list[models.Task] = []
    open_tasks: list[models.Task] = []
    in_progress_details: list[dict] = []

    total_weight = 0.0
    completed_weight = 0.0

    for task in all_tasks:
        if task.status == "done":
            done_at = as_naive(task.completed_at) or as_naive(
                task.updated_at
            )
            if done_at is not None and start <= done_at < end:
                completed_today.append(task)
                completed_weight += 1.0
                total_weight += 1.0
        else:
            open_tasks.append(task)
            done_items, total_items = _task_progress(task)
            if total_items > 0:
                task_progress = done_items / total_items
                completed_weight += task_progress
                total_weight += 1.0
                if done_items > 0:
                    progress_pct = round(100.0 * task_progress)
                    in_progress_details.append(
                        {
                            "title": task.title,
                            "progress": f"{done_items}/{total_items}",
                            "percent": progress_pct,
                        }
                    )
            else:
                total_weight += 1.0

    relevant_total = len(completed_today) + len(open_tasks)
    done_count = len(completed_today)
    percent = 0.0
    if total_weight > 0:
        percent = round(100.0 * completed_weight / total_weight, 1)

    hours: list[int] = []
    for task in completed_today:
        done_at = as_naive(task.completed_at) or as_naive(task.updated_at)
        if done_at is not None:
            hours.append(done_at.hour)

    tomorrow = target + timedelta(days=1)
    tomorrow_start = datetime.combine(tomorrow, datetime.min.time())
    tomorrow_end = tomorrow_start + timedelta(days=1)
    hard_tomorrow: list[str] = []
    overdue_titles: list[str] = []
    now = now_naive()
    for task in open_tasks:
        due = as_naive(task.due_at)
        if due is not None and due < now:
            overdue_titles.append(task.title)
        is_hard = bool(task.is_important)
        if due is not None and tomorrow_start <= due < tomorrow_end:
            if is_hard or bool(task.is_urgent):
                hard_tomorrow.append(task.title)
        elif is_hard and bool(task.is_urgent) and due is None:
            hard_tomorrow.append(task.title)

    stats = {
        "date": target.isoformat(),
        "total_open_and_done_today": relevant_total,
        "completed_count": done_count,
        "completion_percent": percent,
        "most_productive_period": _productive_period(hours),
        "completed_titles": [task.title for task in completed_today],
        "tomorrow_hard_tasks": hard_tomorrow[:5],
        "overdue_titles": overdue_titles[:5],
        "in_progress_tasks": in_progress_details[:5],
    }
    logger.info(
        "Collected digest stats for %s: %s%% complete, %d in progress",
        target.isoformat(),
        percent,
        len(in_progress_details),
    )
    return stats


def _generate_digest_text(stats: dict) -> str:
    """Ask the chat model to write a short coaching digest."""
    period = stats["most_productive_period"] or "нет данных"
    completed = stats["completed_titles"] or ["нет выполненных задач"]
    hard = stats["tomorrow_hard_tasks"] or ["нет сложных задач"]
    overdue = stats["overdue_titles"] or ["нет"]
    in_progress = stats.get("in_progress_tasks", [])

    system_message = (
        "You are a personal productivity coach. Write a short "
        "evening digest in Russian (4-6 sentences). Mention the "
        "completion percent, acknowledge partial progress on tasks "
        "with checklists, mention the most productive period if "
        "known, and give a concrete recommendation for tomorrow. "
        "Be supportive and recognize effort, not just completion. "
        "Use only the provided numbers and titles."
    )

    in_progress_lines = []
    for item in in_progress:
        in_progress_lines.append(
            f"  - {item['title']}: {item['progress']} "
            f"({item['percent']}%)"
        )
    in_progress_str = (
        "\n".join(in_progress_lines) if in_progress_lines else "нет"
    )

    prompt = (
        f"Date: {stats['date']}\n"
        f"Completed today: {stats['completed_count']} of "
        f"{stats['total_open_and_done_today']} "
        f"({stats['completion_percent']}%)\n"
        f"Tasks in progress (with partial checklist completion):\n"
        f"{in_progress_str}\n"
        f"Most productive period: {period}\n"
        f"Completed tasks: {', '.join(completed)}\n"
        f"Hard tasks tomorrow: {', '.join(hard)}\n"
        f"Still overdue: {', '.join(overdue)}"
    )
    return openai_client.chat_completion(
        prompt=prompt,
        system_message=system_message,
        temperature=0.4,
    )


def get_digest(
    db: Session,
    target: date | None = None,
    refresh: bool = False,
) -> dict:
    """Build (or return cached) evening digest for a date.

    Args:
        db: Database session
        target: Date to summarize; defaults to today
        refresh: If True, ignore the in-memory daily cache

    Returns:
        Digest payload with stats, text, and cache flag
    """
    day = target or now_naive().date()
    cache_key = day.isoformat()
    if not refresh and cache_key in _DIGEST_CACHE:
        cached = dict(_DIGEST_CACHE[cache_key])
        cached["cached"] = True
        logger.info("Returning cached digest for %s", cache_key)
        return cached

    stats = collect_day_stats(db, day)
    try:
        text = _generate_digest_text(stats).strip()
    except Exception as exc:
        logger.error("Failed to generate digest text: %s", str(exc))
        raise

    payload = {
        "date": cache_key,
        "text": text,
        "stats": stats,
        "cached": False,
    }
    _DIGEST_CACHE[cache_key] = payload
    logger.info("Generated digest for %s", cache_key)
    return payload
