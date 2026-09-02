"""OpenAI client wrapper for structured API calls."""

import logging
from typing import NoReturn

from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)
from pydantic import BaseModel

from app.config import settings
from app.exceptions import OpenAIServiceError

logger = logging.getLogger(__name__)

# One retry; stay below the frontend 90s request timeout.
OPENAI_TIMEOUT_SECONDS = 40.0

_AUTH_MESSAGE = "Неверный ключ OpenAI. Проверьте OPENAI_API_KEY в .env."
_RATE_LIMIT_MESSAGE = (
    "Превышен лимит запросов к OpenAI. Подождите и повторите."
)
_TIMEOUT_MESSAGE = (
    "Превышено время ожидания ответа OpenAI. Попробуйте ещё раз."
)
_CONNECTION_MESSAGE = "Не удалось связаться с OpenAI. Проверьте сеть."
_GENERIC_MESSAGE = "Сервис OpenAI временно недоступен. Попробуйте позже."


def _raise_openai_service_error(exc: Exception) -> NoReturn:
    """Log an OpenAI failure and raise a user-safe error.

    Args:
        exc: Original exception from the OpenAI SDK

    Raises:
        OpenAIServiceError: Always, with a user-facing message
    """
    logger.error("OpenAI API error: %s", str(exc))
    if isinstance(exc, OpenAIServiceError):
        raise exc
    if isinstance(exc, AuthenticationError):
        raise OpenAIServiceError(
            _AUTH_MESSAGE,
            status_code=502,
        ) from exc
    if isinstance(exc, RateLimitError):
        raise OpenAIServiceError(
            _RATE_LIMIT_MESSAGE,
            status_code=429,
        ) from exc
    if isinstance(exc, (APITimeoutError, TimeoutError)):
        raise OpenAIServiceError(
            _TIMEOUT_MESSAGE,
            status_code=504,
        ) from exc
    if isinstance(exc, APIConnectionError):
        raise OpenAIServiceError(
            _CONNECTION_MESSAGE,
            status_code=502,
        ) from exc
    raise OpenAIServiceError(_GENERIC_MESSAGE, status_code=502) from exc


class OpenAIClient:
    """Wrapper for OpenAI API with structured output support."""

    def __init__(self) -> None:
        """Initialize OpenAI client with API key from settings."""
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            timeout=OPENAI_TIMEOUT_SECONDS,
            max_retries=1,
        )
        self.chat_model = settings.openai_chat_model
        self.embedding_model = settings.embedding_model
        logger.info("OpenAI client initialized with model=%s", self.chat_model)

    def chat_completion(
        self,
        prompt: str,
        system_message: str | None = None,
        temperature: float = 0.7,
    ) -> str:
        """
        Get chat completion from OpenAI.

        Args:
            prompt: User prompt
            system_message: Optional system message
            temperature: Sampling temperature (0-2)

        Returns:
            Response text from the model

        Raises:
            OpenAIServiceError: If the API call fails
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        logger.info("Requesting chat completion")
        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=messages,
                temperature=temperature,
            )
            content = response.choices[0].message.content
            logger.info("Chat completion received successfully")
            return content if content else ""
        except Exception as e:
            _raise_openai_service_error(e)

    def structured_completion(
        self,
        prompt: str,
        response_format: type[BaseModel],
        system_message: str | None = None,
        temperature: float = 0.7,
    ) -> BaseModel:
        """
        Get structured output from OpenAI using JSON schema.

        Args:
            prompt: User prompt
            response_format: Pydantic model for response validation
            system_message: Optional system message
            temperature: Sampling temperature (0-2)

        Returns:
            Validated Pydantic model instance

        Raises:
            OpenAIServiceError: If the API call fails or is empty
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        logger.info(
            "Requesting structured completion with format=%s",
            response_format.__name__,
        )
        try:
            response = self.client.beta.chat.completions.parse(
                model=self.chat_model,
                messages=messages,
                response_format=response_format,
                temperature=temperature,
            )
            parsed = response.choices[0].message.parsed
            if parsed is None:
                raise OpenAIServiceError(
                    "Модель не вернула структурированный ответ."
                )
            logger.info("Structured completion received successfully")
            return parsed
        except OpenAIServiceError:
            raise
        except Exception as e:
            _raise_openai_service_error(e)

    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Get embedding vectors for one or more texts.

        Args:
            texts: Texts to embed

        Returns:
            Embedding vectors in the same order as texts

        Raises:
            OpenAIServiceError: If the API call fails
        """
        if not texts:
            return []

        logger.info("Requesting embeddings for %d texts", len(texts))
        try:
            vectors: list[list[float]] = []
            batch_size = 64
            for start in range(0, len(texts), batch_size):
                batch = texts[start : start + batch_size]
                response = self.client.embeddings.create(
                    model=self.embedding_model,
                    input=batch,
                )
                ordered = sorted(response.data, key=lambda item: item.index)
                vectors.extend(item.embedding for item in ordered)
            logger.info(
                "Embeddings received successfully, count=%d",
                len(vectors),
            )
            return vectors
        except Exception as e:
            _raise_openai_service_error(e)

    def get_embedding(self, text: str) -> list[float]:
        """
        Get embedding vector for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (list of floats)

        Raises:
            OpenAIServiceError: If the API call fails
        """
        embeddings = self.get_embeddings([text])
        return embeddings[0] if embeddings else []


# Singleton instance
openai_client = OpenAIClient()
