"""Application-level exceptions and HTTP mapping."""

from typing import NoReturn

from fastapi import HTTPException, status


class OpenAIServiceError(Exception):
    """User-facing OpenAI API failure.

    Attributes:
        status_code: Suggested HTTP status for the API response.
    """

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_502_BAD_GATEWAY,
    ) -> None:
        """Store a safe message and HTTP status.

        Args:
            message: Message that can be shown to the user
            status_code: HTTP status to return from routers
        """
        super().__init__(message)
        self.status_code = status_code


def raise_openai_http(
    exc: Exception,
    fallback: str | None = None,
) -> NoReturn:
    """Raise HTTPException for an OpenAI-related failure.

    Args:
        exc: Original exception from an AI service call
        fallback: Message if ``exc`` is not OpenAIServiceError

    Raises:
        HTTPException: Always; 502/429/504 for known AI errors
    """
    if isinstance(exc, HTTPException):
        raise exc
    if isinstance(exc, OpenAIServiceError):
        raise HTTPException(
            status_code=exc.status_code,
            detail=str(exc),
        ) from exc
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=fallback
        or ("Не удалось выполнить запрос к OpenAI. " "Попробуйте позже."),
    ) from exc
