"""LiteLLM-backed chat client. No vendor SDKs elsewhere."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from agentic_ai.llm.config import LLMConfig, load_llm_config
from agentic_ai.logging_setup import truncate

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, config: LLMConfig) -> None:
        self.config = config

    @classmethod
    def from_config(cls, path: Path | None = None) -> LLMClient:
        return cls(load_llm_config(path))

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        response_format: dict[str, Any] | None = None,
        label: str = "chat",
    ) -> str:
        import litellm

        model_id = self.config.resolve_model_id()
        logger.info("LLM[%s] → model=%s", label, model_id)
        for msg in messages:
            role = msg.get("role", "?")
            logger.info(
                "LLM[%s] prompt (%s): %s",
                label,
                role,
                truncate(str(msg.get("content", "")), 1200),
            )

        kwargs = self.config.litellm_kwargs()
        kwargs["messages"] = messages
        if response_format is not None:
            kwargs["response_format"] = response_format

        response = litellm.completion(**kwargs)
        content = response.choices[0].message.content
        if content is None:
            content = ""
        else:
            content = str(content)

        logger.info("LLM[%s] ← response: %s", label, truncate(content, 1200))
        return content
