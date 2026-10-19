"""Semantic memory: access to the knowledge base store."""

from pathlib import Path
from typing import Any

from agentic_ai.environment.stores.knowledge_base import KnowledgeBaseStore


class SemanticMemory:
    """Thin wrapper over the knowledge base for agent-facing reads."""

    def __init__(self, store_path: Path | None = None) -> None:
        from agentic_ai.environment.stores.config import StoreConfig

        if store_path is not None:
            config = StoreConfig(
                name="knowledge_base",
                path=store_path,
                collection="documents",
                embedding_model="chroma-default",
            )
            self.store = KnowledgeBaseStore(config)
        else:
            self.store = KnowledgeBaseStore()

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        return self.store.query(query, top_k=top_k)
