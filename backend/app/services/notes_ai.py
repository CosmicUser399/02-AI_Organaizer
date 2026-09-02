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
            "3-5 relevant tags categorizing the note content "
            "(e.g., idea, meeting, research, todo, personal)"
        ),
    )
    summary: str = Field(
        ..., description="Brief 1-2 sentence summary of the note"
    )
    key_topics: list[str] = Field(
        default_factory=list,
        description="Main topics or entities mentioned in the note",
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

    system_message = """You are a note analysis assistant.
Extract relevant tags and key information from notes.

Guidelines:
- tags: Use 3-5 descriptive tags (lowercase, single words or phrases)
- Common tag categories: work, personal, idea, meeting, research,
  todo, learning, finance, health, project, goal
- summary: Concise 1-2 sentence summary capturing main points
- key_topics: Extract main topics, names, or entities mentioned
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
        "Summarize the following text concisely in the same "
        "language. Keep key facts. Return only the summary."
    ),
    "fix_grammar": (
        "Fix grammar, spelling, and punctuation. Keep the same "
        "language, meaning, and approximate length. Return only "
        "the corrected text."
    ),
    "tone_business": (
        "Rewrite the text in a professional business tone. Keep "
        "the same language and meaning. Return only the rewritten "
        "text."
    ),
    "tone_friendly": (
        "Rewrite the text in a friendly, warm tone. Keep the same "
        "language and meaning. Return only the rewritten text."
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
