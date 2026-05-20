from __future__ import annotations

import logging
from typing import Dict, List, Optional

from openai import APIError, OpenAI

from app.config import get_settings

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Thin wrapper around the OpenAI SDK pointed at OpenRouter.

    Tries a chain of free models until one responds successfully; falls back
    to a caller-provided string if every model fails or the service is not
    configured with an API key.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self.settings = settings
        self._client: Optional[OpenAI] = None
        if settings.openrouter_api_key:
            self._client = OpenAI(
                base_url=settings.openrouter_base_url,
                api_key=settings.openrouter_api_key,
                default_headers={
                    "HTTP-Referer": settings.app_url,
                    "X-Title": settings.app_name,
                },
            )

    @property
    def configured(self) -> bool:
        return self._client is not None

    @property
    def primary_model(self) -> str:
        return self.settings.models[0] if self.settings.models else "openrouter/free"

    def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        fallback: str,
        temperature: float = 0.4,
        max_tokens: int = 1200,
        response_format: Optional[Dict[str, str]] = None,
    ) -> str:
        if not self._client:
            logger.warning("OpenRouter not configured — returning fallback response.")
            return fallback

        last_error: Optional[Exception] = None
        for model in self.settings.models:
            try:
                kwargs: Dict[str, object] = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
                if response_format is not None:
                    kwargs["response_format"] = response_format

                resp = self._client.chat.completions.create(**kwargs)
                content = (resp.choices[0].message.content or "").strip()
                if content:
                    return content
                logger.warning("Empty content from model %s", model)
            except APIError as e:
                last_error = e
                logger.warning("OpenRouter API error on %s: %s", model, e)
            except Exception as e:  # noqa: BLE001 - we want to catch any transport error
                last_error = e
                logger.warning("OpenRouter general error on %s: %s", model, e)

        if last_error is not None:
            logger.error("All OpenRouter models failed; using fallback. Last error: %s", last_error)
        return fallback


# Module-level singleton so every route shares one HTTP client.
_llm: Optional[LLMClient] = None


def get_llm() -> LLMClient:
    global _llm
    if _llm is None:
        _llm = LLMClient()
    return _llm
