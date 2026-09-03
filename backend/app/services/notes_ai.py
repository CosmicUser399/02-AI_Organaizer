"""AI service for notes: auto-tagging and linking."""

import logging
from typing import Optional

from pydantic import BaseModel, Field

from app.services.openai_client import openai_client

logger = logging.getLogger(__name__)


class NoteAnalysis(BaseModel):
    """Structured output for note analysis."""

    tags: list[str] = Field(
        ...,
        description=(
            "3-5 релевантных тегов, категоризирующих содержание заметки "
            "(например, идея, встреча, исследование, задача, личное)"
        ),
    )
    summary: str = Field(
        ..., description="Краткое резюме заметки в 1-2 предложениях"
    )
    key_topics: list[str] = Field(
        default_factory=list,
        description="Основные темы или объекты, упомянутые в заметке",
    )


def analyze_note(title: str, content: str) -> NoteAnalysis:
    """
    Analyze note content to extract tags and key information.

    Uses OpenAI to automatically tag notes and extract
    key topics for better organization and searchability.

    Args:
        title: Note title
        content: Note content

    Returns:
        NoteAnalysis with tags, summary, and key topics

    Raises:
        Exception: If OpenAI API call fails
    """
    logger.info("Analyzing note: %s", title)

    system_message = """Ты — помощник по анализу заметок.
Извлекай релевантные теги и ключевую информацию из заметок.

Рекомендации:
- tags: Используй 3-5 описательных тегов (строчными буквами,
  одно слово или фразы)
- Общие категории тегов: работа, личное, идея, встреча, исследование,
  задача, обучение, финансы, здоровье, проект, цель
- summary: Краткое резюме в 1-2 предложениях, отражающее основные моменты
- key_topics: Извлеки основные темы, имена или объекты, упомянутые в заметке
"""

    note_text = f"Title: {title}\n\nContent: {content}"

    try:
        analysis = openai_client.structured_completion(
            prompt=note_text,
            response_format=NoteAnalysis,
            system_message=system_message,
            temperature=0.3,
        )
        logger.info(
            "Note analyzed successfully: %d tags extracted", len(analysis.tags)
        )
        return analysis
    except Exception as e:
        logger.error("Failed to analyze note: %s", str(e))
        raise


def suggest_task_link(
    note_title: str,
    note_content: str,
    task_title: str,
    task_description: Optional[str] = None,
) -> float:
    """
    Calculate relevance score between note and task.

    Uses simple text similarity to suggest if a note
    should be linked to a task.

    Args:
        note_title: Note title
        note_content: Note content
        task_title: Task title
        task_description: Optional task description

    Returns:
        Relevance score between 0 and 1
    """
    note_text = f"{note_title} {note_content}".lower()
    task_text = f"{task_title} {task_description or ''}".lower()

    words_note = set(note_text.split())
    words_task = set(task_text.split())

    if not words_note or not words_task:
        return 0.0

    common_words = words_note.intersection(words_task)
    relevance = len(common_words) / max(len(words_note), len(words_task))

    return min(relevance * 2, 1.0)


TRANSFORM_MODES = (
    "summarize",
    "fix_grammar",
    "tone_business",
    "tone_friendly",
)

_TRANSFORM_INSTRUCTIONS = {
    "summarize": (
        "Сделай краткое резюме следующего текста на том же языке. "
        "Сохрани ключевые факты. Верни только резюме."
    ),
    "fix_grammar": (
        "Исправь грамматику, орфографию и пунктуацию. Сохрани тот же "
        "язык, смысл и примерную длину. Верни только исправленный текст."
    ),
    "tone_business": (
        "Перепиши текст в профессиональном деловом тоне. Сохрани "
        "тот же язык и смысл. Верни только переписанный текст."
    ),
    "tone_friendly": (
        "Перепиши текст в дружелюбном, теплом тоне. Сохрани тот же "
        "язык и смысл. Верни только переписанный текст."
    ),
}


def transform_text(selection: str, mode: str) -> str:
    """Transform a selected note fragment with the chat model.

    Args:
        selection: Highlighted text from a note
        mode: One of TRANSFORM_MODES

    Returns:
        Transformed text

    Raises:
        ValueError: If mode is unknown or selection is empty
        Exception: If OpenAI API call fails
    """
    cleaned = selection.strip()
    if not cleaned:
        raise ValueError("Selection is empty")
    if mode not in _TRANSFORM_INSTRUCTIONS:
        raise ValueError(f"Unknown transform mode: {mode}")

    logger.info("Transforming text with mode=%s", mode)
    system_message = _TRANSFORM_INSTRUCTIONS[mode]
    result = openai_client.chat_completion(
        prompt=cleaned,
        system_message=system_message,
        temperature=0.3,
    )
    transformed = (result or "").strip()
    if not transformed:
        raise ValueError("Model returned empty transform result")
    logger.info("Text transformed successfully, mode=%s", mode)
    return transformed
