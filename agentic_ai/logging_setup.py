"""Configure application logging from config/logging.yaml."""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from agentic_ai.paths import CONFIG_DIR

_CONFIGURED = False


def setup_logging(path: Path | None = None) -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    config_path = path or (CONFIG_DIR / "logging.yaml")
    level_name = "INFO"
    fmt = "%(asctime)s %(levelname)s %(name)s — %(message)s"
    if config_path.is_file():
        with config_path.open(encoding="utf-8") as fh:
            raw = yaml.safe_load(fh) or {}
        level_name = str(raw.get("level", level_name))
        fmt = str(raw.get("format", fmt))

    level = getattr(logging, level_name.upper(), logging.INFO)
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(level=level, format=fmt)
    else:
        root.setLevel(level)
        for handler in root.handlers:
            handler.setFormatter(logging.Formatter(fmt))

    # Keep noisy libs quieter so LLM thought process stays readable
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("LiteLLM").setLevel(logging.WARNING)
    logging.getLogger("litellm").setLevel(logging.WARNING)

    _CONFIGURED = True


def truncate(text: str, limit: int = 800) -> str:
    text = text or ""
    if len(text) <= limit:
        return text
    return text[:limit] + f"… [{len(text) - limit} more chars]"
