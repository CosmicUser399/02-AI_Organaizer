"""OpenAI client wrapper for structured API calls."""

import logging
from typing import Any

from openai import OpenAI
from pydantic import BaseModel

from app.config import settings

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Wrapper for OpenAI API with structured output support."""

    def __init__(self) -> None:
        """Initialize OpenAI client with API key from settings."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.chat_model = settings.openai_chat_model
        self.embedding_model = settings.embedding_model
        logger.info(
            "OpenAI client initialized with model=%s",
            self.chat_model
        )

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
            logger.error("OpenAI API error: %s", str(e))
            raise

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
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        logger.info(
            "Requesting structured completion with format=%s",
            response_format.__name__
        )
        try:
            response = self.client.beta.chat.completions.parse(
                model=self.chat_model,
                messages=messages,
                response_format=response_format,
                temperature=temperature,
            )
            parsed = response.choices[0].message.parsed
            logger.info("Structured completion received successfully")
            return parsed
        except Exception as e:
            logger.error("OpenAI API error: %s", str(e))
            raise

    def get_embedding(self, text: str) -> list[float]:
        """
        Get embedding vector for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (list of floats)
        """
        logger.info("Requesting embedding for text")
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text,
            )
            embedding = response.data[0].embedding
            logger.info(
                "Embedding received successfully, dimension=%d",
                len(embedding)
            )
            return embedding
        except Exception as e:
            logger.error("OpenAI API error: %s", str(e))
            raise


# Singleton instance
openai_client = OpenAIClient()
