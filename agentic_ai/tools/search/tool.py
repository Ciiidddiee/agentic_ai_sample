"""Search tool: query a store and return ranked hits."""

from __future__ import annotations

from typing import Any

from agentic_ai.environment.stores.config import load_store_config
from agentic_ai.environment.stores.knowledge_base import KnowledgeBaseStore


def search(
    query: str,
    store: str = "knowledge_base",
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Query a named store.

    Hit shape: id, score, snippet, metadata
    """
    if not query or not query.strip():
        return []
    config = load_store_config(store)
    kb = KnowledgeBaseStore(config)
    return kb.query(query.strip(), top_k=top_k)
