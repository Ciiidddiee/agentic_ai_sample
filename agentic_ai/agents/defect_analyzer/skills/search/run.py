"""Search prior defect cases in the shared store."""

from __future__ import annotations

import logging
from typing import Any

from agentic_ai.shared.environment.stores.knowledge_base import KnowledgeBaseStore

logger = logging.getLogger(__name__)


def search_prior_defects(
    query: str,
    *,
    top_k: int = 5,
    prefer_defect: bool = True,
    store: KnowledgeBaseStore | None = None,
) -> list[dict[str, Any]]:
    """Query KB; optionally rank kind=defect hits first."""
    if not query or not query.strip():
        return []
    kb = store or KnowledgeBaseStore()
    fetch_k = top_k * 2 if prefer_defect else top_k
    hits = kb.query(query.strip()[:4000], top_k=fetch_k)
    if prefer_defect:
        hits = sorted(
            hits,
            key=lambda h: (
                0 if (h.get("metadata") or {}).get("kind") == "defect" else 1,
                -float(h.get("score") or 0.0),
            ),
        )
    hits = hits[:top_k]
    logger.info("defect search: %s hit(s)", len(hits))
    return hits
