"""Load and render markdown prompt templates."""

from __future__ import annotations

from pathlib import Path


def load_prompt(path: Path, **variables: object) -> str:
    """Read a prompt file and replace ``{name}`` placeholders with values."""
    text = Path(path).read_text(encoding="utf-8")
    for key, value in variables.items():
        text = text.replace("{" + key + "}", str(value))
    return text.strip()
