"""Task decomposition service using OpenAI."""

import logging
from typing import Optional

from pydantic import BaseModel, Field

from app.services.openai_client import openai_client

logger = logging.getLogger(__name__)


class DecomposedTask(BaseModel):
    """Structured output for task decomposition."""

    checklist_items: list[str] = Field(
        ..., description="List of actionable steps to complete the task"
    )
    suggestions: list[str] = Field(
        default_factory=list,
        description=(
            "Contextual suggestions: potential blockers, "
            "additional subtasks, or things to consider"
        ),
    )


def decompose_task(
    title: str,
    description: Optional[str] = None,
) -> DecomposedTask:
    """
    Decompose task into checklist items and suggestions.

    Uses OpenAI to break down a task into actionable steps
    and provides contextual suggestions for better execution.

    Args:
        title: Task title
        description: Optional task description with more context

    Returns:
        DecomposedTask with checklist items and suggestions

    Raises:
        Exception: If OpenAI API call fails
    """
    logger.info("Decomposing task: %s", title)

    system_message = """You are an intelligent task decomposition assistant.
Break down tasks into clear, actionable steps and provide helpful context.

Guidelines for checklist_items:
- Create 3-7 concrete, actionable steps
- Start each step with a verb (e.g., "Research", "Draft", "Review")
- Order steps logically from first to last
- Make steps specific and testable
- Keep each step focused on one action

Guidelines for suggestions:
- Identify potential blockers or dependencies
- Suggest additional subtasks that might be helpful
- Mention tools, resources, or approaches to consider
- Highlight things that are easy to overlook
- Keep suggestions brief and actionable
"""

    task_context = f"Task: {title}"
    if description:
        task_context += f"\nDescription: {description}"

    try:
        decomposed = openai_client.structured_completion(
            prompt=task_context,
            response_format=DecomposedTask,
            system_message=system_message,
            temperature=0.5,
        )
        logger.info(
            "Task decomposed successfully: %d steps, %d suggestions",
            len(decomposed.checklist_items),
            len(decomposed.suggestions),
        )
        return decomposed
    except Exception as e:
        logger.error("Failed to decompose task: %s", str(e))
        raise
