"""Load LLM settings from config/model.yaml."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from agentic_ai.paths import CONFIG_DIR

_PROVIDER_KEY_ENV = {
    "groq": "GROQ_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "openai_compatible": "INTERNAL_LLM_API_KEY",
}


@dataclass(frozen=True)
class LLMConfig:
    provider: str
    model: str
    temperature: float = 0.2
    model_id: str | None = None
    base_url: str | None = None
    api_key_env: str | None = None
    timeout_seconds: int = 60

    def resolve_model_id(self) -> str:
        if self.model_id:
            return self.model_id
        if self.provider == "openai_compatible":
            return f"openai/{self.model}"
        return f"{self.provider}/{self.model}"

    def resolve_api_key(self) -> str | None:
        env_name = self.api_key_env or _PROVIDER_KEY_ENV.get(self.provider)
        if not env_name:
            return None
        return os.getenv(env_name) or None

    def litellm_kwargs(self) -> dict[str, Any]:
        """Build kwargs for litellm.completion (excluding messages)."""
        kwargs: dict[str, Any] = {
            "model": self.resolve_model_id(),
            "temperature": self.temperature,
            "timeout": self.timeout_seconds,
        }
        api_key = self.resolve_api_key()
        if api_key:
            kwargs["api_key"] = api_key
        if self.base_url:
            kwargs["api_base"] = self.base_url
        elif self.provider == "openai_compatible":
            raise ValueError(
                "provider openai_compatible requires base_url in config/model.yaml"
            )
        return kwargs


def load_llm_config(path: Path | None = None) -> LLMConfig:
    config_path = path or (CONFIG_DIR / "model.yaml")
    with config_path.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    return LLMConfig(
        provider=str(raw.get("provider", "groq")),
        model=str(raw.get("model", "llama-3.3-70b-versatile")),
        temperature=float(raw.get("temperature", 0.2)),
        model_id=raw.get("model_id"),
        base_url=raw.get("base_url"),
        api_key_env=raw.get("api_key_env"),
        timeout_seconds=int(raw.get("timeout_seconds", 60)),
    )
