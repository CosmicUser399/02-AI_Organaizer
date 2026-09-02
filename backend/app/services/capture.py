"""Magic Input capture service using OpenAI."""

import logging
from datetime import datetime

from pydantic import BaseModel, Field

from app.services.openai_client import openai_client

logger = logging.getLogger(__name__)


class ParsedTask(BaseModel):
    """Structured output from Magic Input parsing."""

    title: str = Field(..., description="Short task title (max 100 chars)")
    description: str | None = Field(
        None, description="Detailed task description or context"
    )
    due_at: datetime | None = Field(
        None, description="Due date/time in ISO format if mentioned"
    )
    tag: str | None = Field(
        None,
        description=(
            "Category tag: work, personal, health, learning, "
            "finance, shopping, other"
        ),
    )
    is_urgent: bool = Field(
        False, description="True if requires immediate attention"
    )
    is_important: bool = Field(
        False, description="True if has significant impact/consequences"
    )


def parse_magic_input(raw_input: str) -> ParsedTask:
    """
    Parse natural language input into structured task.

    Uses OpenAI to extract task details from free-form text,
    including title, description, deadline, priority markers,
    and category tag.

    Args:
        raw_input: Natural language task description

    Returns:
        ParsedTask with extracted fields

    Raises:
        Exception: If OpenAI API call fails
    """
    logger.info("Parsing magic input: %s", raw_input[:50])

    system_message = """You are an intelligent task parser.
Extract structured task information from natural language input.

Guidelines:
- title: Make it concise and actionable (verb + object)
- description: Extract additional context, requirements, notes
- due_at: Parse relative dates (today, tomorrow, next week, etc.)
         and absolute dates. Use ISO format with current timezone.
- tag: Categorize as work/personal/health/learning/finance/shopping
       or other
- is_urgent: True if words like "urgent", "ASAP", "immediately",
            "critical" appear or deadline is very soon
- is_important: True if task has significant consequences, affects
               others, or relates to goals/priorities

Current datetime: {now}
""".format(
        now=datetime.now().isoformat()
    )

    try:
        parsed = openai_client.structured_completion(
            prompt=raw_input,
            response_format=ParsedTask,
            system_message=system_message,
            temperature=0.3,
        )
        logger.info(
            "Magic input parsed successfully: title='%s'", parsed.title
        )
        return parsed
    except Exception as e:
        logger.error("Failed to parse magic input: %s", str(e))
        raise
