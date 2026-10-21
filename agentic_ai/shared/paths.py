"""Project root and data path helpers."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# shared/paths.py → shared → agentic_ai package → project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"


def data_dir() -> Path:
    raw = os.getenv("DATA_DIR", str(PROJECT_ROOT / "data"))
    path = Path(raw)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


def ensure_data_dirs() -> dict[str, Path]:
    root = data_dir()
    dirs = {
        "root": root,
        "raw": root / "raw",
        "processed": root / "processed",
        "knowledge_base": root / "knowledge_base",
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return dirs
