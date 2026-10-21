"""Analyze a defect report with optional prior case context."""

from __future__ import annotations

import logging
from typing import Any

from agentic_ai.agents.defect_analyzer.prompts import load as load_prompt
from agentic_ai.agents.defect_analyzer.prompts import system_prompt
from agentic_ai.shared.llm.client import LLMClient
from agentic_ai.shared.util.json_extract import parse_json_object

logger = logging.getLogger(__name__)


def analyze_defect(
    document_text: str,
    prior_documents: list[dict[str, Any]] | None = None,
    *,
    llm: LLMClient | None = None,
) -> dict[str, Any]:
    prior_documents = prior_documents or []
    prior_ids = [str(d.get("id")) for d in prior_documents]
    logger.info(
        "analyze_defect: prior_docs=%s chars=%s",
        prior_ids or "none",
        len(document_text or ""),
    )

    prior_block = ""
    for doc in prior_documents:
        prior_block += (
            f"\n--- prior id={doc.get('id')} ---\n"
            f"{(doc.get('text') or '')[:2000]}\n"
        )

    user_prompt = load_prompt(
        "analyze_defect",
        document_text=(document_text or "")[:6000],
        prior_block=prior_block or "(none)",
    )

    client = llm or LLMClient.from_config()
    raw = client.chat(
        [
            {"role": "system", "content": system_prompt()},
            {"role": "user", "content": user_prompt},
        ],
        label="analyze_defect",
    )
    parsed = parse_json_object(raw)
    findings = parsed.get("findings") or []
    if not isinstance(findings, list):
        findings = [str(findings)]
    citations = parsed.get("citations") or []
    if not isinstance(citations, list):
        citations = []
    severity = str(parsed.get("severity", "unknown")).lower()
    if severity not in {"low", "medium", "high", "unknown"}:
        severity = "unknown"
    result = {
        "summary": str(parsed.get("summary", "")),
        "findings": [str(f) for f in findings],
        "severity": severity,
        "citations": [str(c) for c in citations],
    }
    logger.info(
        "analyze_defect done: severity=%s summary=%r findings=%s citations=%s",
        result["severity"],
        (result["summary"][:200] + "…")
        if len(result["summary"]) > 200
        else result["summary"],
        result["findings"],
        result["citations"],
    )
    return result
