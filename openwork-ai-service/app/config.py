from __future__ import annotations

import os
from functools import lru_cache
from typing import List

from dotenv import load_dotenv

load_dotenv()


# Reasonable free-tier defaults (all verified on OpenRouter free list).
# Order matters: first is primary, the rest are fallbacks tried in sequence.
DEFAULT_MODELS: List[str] = [
    "openai/gpt-oss-120b:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "openrouter/free",
]


class Settings:
    def __init__(self) -> None:
        self.openrouter_api_key: str | None = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_base_url: str = os.getenv(
            "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
        )
        self.app_url: str = os.getenv("OPENROUTER_APP_URL", "https://openwork.local")
        self.app_name: str = os.getenv("OPENROUTER_APP_NAME", "OpenWork AI Service")

        raw_models = os.getenv("OPENROUTER_MODELS", "").strip()
        if raw_models:
            self.models: List[str] = [m.strip() for m in raw_models.split(",") if m.strip()]
        else:
            self.models = list(DEFAULT_MODELS)

        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")

    @property
    def configured(self) -> bool:
        return bool(self.openrouter_api_key)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
