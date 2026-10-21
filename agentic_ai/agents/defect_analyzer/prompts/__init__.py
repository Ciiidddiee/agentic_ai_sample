"""DefectAnalyzer prompt templates (loaded at runtime)."""

from __future__ import annotations

from pathlib import Path

from agentic_ai.shared.util.prompts import load_prompt

PROMPTS_DIR = Path(__file__).resolve().parent


def load(name: str, **variables: object) -> str:
    """Load ``prompts/{name}.md`` and fill ``{placeholders}``."""
    path = PROMPTS_DIR / name
    if path.suffix != ".md":
        path = PROMPTS_DIR / f"{name}.md"
    return load_prompt(path, **variables)


def system_prompt() -> str:
    """Agent identity + JSON-only instruction for LLM skills."""
    body = load("system")
    return f"{body}\n\nAlways respond with valid JSON only when a skill asks for JSON."
