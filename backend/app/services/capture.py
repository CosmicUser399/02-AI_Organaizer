"""Magic Input capture service using OpenAI."""

import logging
from datetime import datetime

from pydantic import BaseModel, Field

from app.services.openai_client import openai_client

logger = logging.getLogger(__name__)


class ParsedTask(BaseModel):
    """Structured output from Magic Input parsing."""

    title: str = Field(
        ..., description="Краткий заголовок задачи (не более 100 символов)"
    )
    description: str | None = Field(
        None, description="Подробное описание задачи или контекст"
    )
    due_at: datetime | None = Field(
        None, description="Дата и время выполнения в формате ISO"
    )
    tag: str | None = Field(
        None,
        description=(
            "Тег категории: работа, личное, здоровье, обучение, "
            "финансы, покупки, другое"
        ),
    )
    is_urgent: bool = Field(
        False, description="True если требуется немедленное внимание"
    )
    is_important: bool = Field(
        False, description="True если имеет значительное влияние/последствия"
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

    system_message = """Ты — интеллектуальный парсер задач.
Извлекай структурированную информацию о задаче из текста на естественном языке.

Рекомендации:
- title: Сделай заголовок кратким и действенным (глагол + объект)
- description: Извлеки дополнительный контекст, требования, заметки
- due_at: Распознавай относительные даты (сегодня, завтра, через неделю и т.д.)
         и абсолютные даты. Используй ISO формат с текущим часовым поясом.
- tag: Категоризируй как работа/личное/здоровье/обучение/финансы/покупки
       или другое
- is_urgent: True если встречаются слова "срочно", "ASAP", "немедленно",
            "критично" или срок очень скоро
- is_important: True если задача имеет значительные последствия, влияет
               на других или связана с целями/приоритетами

Текущие дата и время: {now}
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
