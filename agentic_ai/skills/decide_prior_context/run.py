"""Decide whether search hits should be used as prior context."""

from __future__ import annotations

import logging
from typing import Any

from agentic_ai.llm.client import LLMClient
from agentic_ai.util.json_extract import parse_json_object
from agentic_ai.util.policy import load_policy

logger = logging.getLogger(__name__)


def decide_prior_context(
    hits: list[dict[str, Any]],
    document_text: str = "",
    *,
    llm: LLMClient | None = None,
    min_score: float | None = None,
) -> dict[str, Any]:
    policy = load_policy()
    prior = policy.get("prior_context") or {}
    threshold = float(min_score if min_score is not None else prior.get("min_score", 0.75))
    on_low = str(prior.get("on_low_confidence", "ask"))

    if not hits:
        result = {
            "decision": "skip",
            "document_ids": [],
            "reason": "No candidates",
        }
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

    if top_score < threshold and on_low in {"ask", "skip", "use"}:
        if top_score < threshold * 0.5:
            result = {
                "decision": on_low if on_low != "use" else "ask",
                "document_ids": [top["id"]] if on_low == "ask" else [],
                "reason": f"Top score {top_score:.2f} well below threshold {threshold:.2f}",
            }
            logger.info("decide_prior_context (rule, very low score): %s", result)
            return result

    client = llm or LLMClient.from_config()
    hits_payload = [
        {
            "id": h.get("id"),
            "score": h.get("score"),
            "snippet": (h.get("snippet") or "")[:300],
            "metadata": h.get("metadata") or {},
        }
        for h in hits[:5]
    ]
    prompt = f"""You decide whether prior documents should be used as context for analyzing a new PDF.

Policy:
- min_score: {threshold}
- on_low_confidence default: {on_low}

Current document (truncated):
\"\"\"
{document_text[:2500]}
\"\"\"

Search hits (JSON):
{hits_payload}

Return ONLY a JSON object with keys:
- decision: one of "use", "skip", "ask"
- document_ids: array of ids to use (empty if skip)
- reason: short explanation

Rules:
- If nothing is relevant, decision=skip.
- If relevance is unclear or scores are near the threshold, decision=ask.
- If clearly relevant and score >= min_score, decision=use and include those ids.
"""
    raw = client.chat(
        [
            {"role": "system", "content": "You return only valid JSON."},
            {"role": "user", "content": prompt},
        ],
        label="decide_prior_context",
    )
    parsed = parse_json_object(raw)
    decision = str(parsed.get("decision", "ask")).lower()
    if decision not in {"use", "skip", "ask"}:
        decision = "ask"
    ids = parsed.get("document_ids") or []
    if not isinstance(ids, list):
        ids = []
    ids = [str(i) for i in ids]
    result = {
        "decision": decision,
        "document_ids": ids,
        "reason": str(parsed.get("reason", "")),
    }
    logger.info("decide_prior_context (llm): %s", result)
    return result
