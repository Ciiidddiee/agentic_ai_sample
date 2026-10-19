"""Load config/policy.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from agentic_ai.paths import CONFIG_DIR


def load_policy(path: Path | None = None) -> dict[str, Any]:
    config_path = path or (CONFIG_DIR / "policy.yaml")
    with config_path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}
