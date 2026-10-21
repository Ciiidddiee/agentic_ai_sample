"""Load store settings from config/stores.yaml."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from agentic_ai.shared.paths import CONFIG_DIR, PROJECT_ROOT, data_dir


@dataclass(frozen=True)
class StoreConfig:
    name: str
    path: Path
    collection: str
    embedding_model: str


def load_store_config(store_name: str | None = None) -> StoreConfig:
    config_path = CONFIG_DIR / "stores.yaml"
    with config_path.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    name = store_name or raw.get("default_store", "knowledge_base")
    stores = raw.get("stores") or {}
    if name not in stores:
        raise KeyError(f"Unknown store: {name}")
    entry = stores[name]
    path = Path(entry.get("path", f"data/{name}"))
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    # Prefer DATA_DIR override for knowledge_base root layout
    if name == "knowledge_base":
        path = data_dir() / "knowledge_base"
    return StoreConfig(
        name=name,
        path=path,
        collection=str(entry.get("collection", "documents")),
        embedding_model=str(entry.get("embedding_model", "chroma-default")),
    )
