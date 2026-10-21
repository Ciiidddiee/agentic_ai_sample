"""Decide whether prior KB hits are strong enough to use (use) or ask a human."""

from __future__ import annotations

import logging
from typing import Any

from agentic_ai.agents.defect_analyzer.prompts import load as load_prompt
from agentic_ai.agents.defect_analyzer.prompts import system_prompt
from agentic_ai.shared.llm.client import LLMClient
from agentic_ai.shared.util.json_extract import parse_json_object
from agentic_ai.shared.util.policy import load_policy

logger = logging.getLogger(__name__)

# Human choices when the agent returns decision=ask
ASK_OPTIONS = ("continue", "ingest", "drop", "use")


def _ask_result(
    reason: str,
    *,
    document_ids: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "decision": "ask",
        "document_ids": list(document_ids or []),
        "reason": reason,
        "options": list(ASK_OPTIONS),
    }


def decide_prior_context(
    hits: list[dict[str, Any]],
    document_text: str = "",
    *,
    llm: LLMClient | None = None,
    min_score: float | None = None,
) -> dict[str, Any]:
    """Return ``use`` or ``ask`` only.

    Low / empty / unclear matches → ask. The human then picks among
    ``ASK_OPTIONS`` (continue = analyze alone, ingest, drop, use).
    Legacy LLM ``skip`` is mapped to ``ask``.
    """
    policy = load_policy()
    prior = policy.get("prior_context") or {}
    threshold = float(min_score if min_score is not None else prior.get("min_score", 0.75))

    if not hits:
        result = _ask_result("No candidates — choose continue, ingest, drop, or use")
        logger.info("decide_prior_context (rule): %s", result)
        return result

    top = hits[0]
    top_score = float(top.get("score", 0.0))
    logger.info(
        "decide_prior_context: %s hit(s), top_id=%s top_score=%.3f threshold=%.2f",
        len(hits),
        top.get("id"),
        top_score,
        threshold,
    )

    # Very low similarity → always ask (no automatic skip/analyze)
    if top_score < threshold * 0.5:
        result = _ask_result(
            f"Top score {top_score:.2f} well below threshold {threshold:.2f}",
            document_ids=[str(top["id"])],
        )
        logger.info("decide_prior_context (rule, very low score): %s", result)
        return result

    hits_payload = [
        {
            "id": h.get("id"),
            "score": h.get("score"),
            "snippet": (h.get("snippet") or "")[:300],
            "metadata": h.get("metadata") or {},
        }
        for h in hits[:5]
    ]
    user_prompt = load_prompt(
        "decide_prior_context",
        threshold=threshold,
        document_text=(document_text or "")[:2500],
        hits_payload=hits_payload,
    )

    client = llm or LLMClient.from_config()
    raw = client.chat(
        [
            {"role": "system", "content": system_prompt()},
            {"role": "user", "content": user_prompt},
        ],
        label="decide_prior_context",
    )
    parsed = parse_json_object(raw)
    decision = str(parsed.get("decision", "ask")).lower()
    # Agent only emits use | ask; map legacy skip → ask
    if decision == "skip":
        decision = "ask"
    if decision not in {"use", "ask"}:
        decision = "ask"
    ids = parsed.get("document_ids") or []
    if not isinstance(ids, list):
        ids = []
    ids = [str(i) for i in ids]

    if decision == "ask":
        result = _ask_result(str(parsed.get("reason", "")), document_ids=ids)
    else:
        result = {
            "decision": "use",
            "document_ids": ids,
            "reason": str(parsed.get("reason", "")),
        }
    logger.info("decide_prior_context (llm): %s", result)
    return result
