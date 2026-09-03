"""Task decomposition service using OpenAI."""

import logging
from typing import Optional

from pydantic import BaseModel, Field

from app.services.openai_client import openai_client

logger = logging.getLogger(__name__)


class DecomposedTask(BaseModel):
    """Structured output for task decomposition."""

    checklist_items: list[str] = Field(
        ..., description="Список действенных шагов для выполнения задачи"
    )
    suggestions: list[str] = Field(
        default_factory=list,
        description=(
            "Контекстные подсказки: потенциальные блокеры, "
            "дополнительные подзадачи или моменты для рассмотрения"
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

    system_message = """Ты — интеллектуальный помощник по декомпозиции задач.
Разбивай задачи на понятные, действенные шаги и предоставляй полезный контекст.

Рекомендации для checklist_items:
- Создай 3-7 конкретных, действенных шагов
- Начинай каждый шаг с глагола (например, "Изучить",
  "Подготовить", "Проверить")
- Расположи шаги логически от первого к последнему
- Делай шаги конкретными и проверяемыми
- Каждый шаг должен быть сфокусирован на одном действии

Рекомендации для suggestions:
- Выяви потенциальные блокеры или зависимости
- Предложи дополнительные подзадачи, которые могут быть полезны
- Укажи инструменты, ресурсы или подходы для рассмотрения
- Выдели моменты, которые легко упустить
- Делай подсказки краткими и действенными
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
