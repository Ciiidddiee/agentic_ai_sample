"""Analyze a PDF with optional prior document context."""

from __future__ import annotations

import logging
from typing import Any

from agentic_ai.llm.client import LLMClient
from agentic_ai.util.json_extract import parse_json_object

logger = logging.getLogger(__name__)


def analyze_pdf(
    document_text: str,
    prior_documents: list[dict[str, Any]] | None = None,
    *,
    llm: LLMClient | None = None,
) -> dict[str, Any]:
    prior_documents = prior_documents or []
    prior_ids = [str(d.get("id")) for d in prior_documents]
    logger.info(
        "analyze_pdf: prior_docs=%s chars=%s",
        prior_ids or "none",
        len(document_text or ""),
    )

    prior_block = ""
    for doc in prior_documents:
        prior_block += (
            f"\n--- prior id={doc.get('id')} ---\n"
            f"{(doc.get('text') or '')[:2000]}\n"
        )

    client = llm or LLMClient.from_config()
    prompt = f"""Analyze the uploaded document. Use prior documents only if provided.

Uploaded document:
\"\"\"
{document_text[:6000]}
\"\"\"

Prior documents:
{prior_block or "(none)"}

Return ONLY a JSON object with keys:
- summary: string
- findings: array of short strings
- citations: array of prior document ids actually used (empty if none)
"""
    raw = client.chat(
        [
            {"role": "system", "content": "You return only valid JSON."},
            {"role": "user", "content": prompt},
        ],
        label="analyze_pdf",
    )
    parsed = parse_json_object(raw)
    findings = parsed.get("findings") or []
    if not isinstance(findings, list):
        findings = [str(findings)]
    citations = parsed.get("citations") or []
    if not isinstance(citations, list):
        citations = []
    result = {
        "summary": str(parsed.get("summary", "")),
        "findings": [str(f) for f in findings],
        "citations": [str(c) for c in citations],
    }
    logger.info(
        "analyze_pdf done: summary=%r findings=%s citations=%s",
        (result["summary"][:200] + "…") if len(result["summary"]) > 200 else result["summary"],
        result["findings"],
        result["citations"],
    )
    return result
