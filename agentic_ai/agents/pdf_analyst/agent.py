"""PDF analyst agent: perceive → decide → act loop."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from agentic_ai.environment.stores.knowledge_base import KnowledgeBaseStore
from agentic_ai.llm.client import LLMClient
from agentic_ai.skills.analyze_pdf.run import analyze_pdf
from agentic_ai.skills.decide_prior_context.run import decide_prior_context
from agentic_ai.tools.ingest.pipeline import ingest
from agentic_ai.tools.ocr.tool import run_ocr
from agentic_ai.tools.search.tool import search

logger = logging.getLogger(__name__)


class PdfAnalystAgent:
    """Upload → OCR → search → decide prior context → analyze."""

    def __init__(
        self,
        llm: LLMClient | None = None,
        *,
        auto_ingest: bool = True,
        top_k: int = 5,
    ) -> None:
        self.llm = llm
        self.auto_ingest = auto_ingest
        self.top_k = top_k

    def run(self, document_path: Path) -> dict[str, Any]:
        """Execute the full analysis flow for one uploaded PDF."""
        path = Path(document_path)
        logger.info("agent start: %s", path)

        ocr = run_ocr(path)
        text = ocr["text"]
        logger.info(
            "perception/OCR: pages=%s confidence=%.2f chars=%s",
            len(ocr["pages"]),
            ocr["confidence"],
            len(text),
        )

        hits = search(text[:4000], store="knowledge_base", top_k=self.top_k)
        logger.info(
            "perception/search: %s hit(s) %s",
            len(hits),
            [(h.get("id"), round(float(h.get("score", 0)), 3)) for h in hits],
        )

        decision = decide_prior_context(
            hits,
            document_text=text,
            llm=self.llm,
        )
        logger.info("decision: %s", decision)

        result: dict[str, Any] = {
            "document_path": str(path),
            "ocr": {
                "confidence": ocr["confidence"],
                "page_count": len(ocr["pages"]),
            },
            "hits": hits,
            "decision": decision,
            "analysis": None,
            "ingest": None,
            "status": "ok",
        }

        if decision["decision"] == "ask":
            result["status"] = "needs_input"
            logger.info("agent stop: needs_input (ask)")
            return result

        prior_docs: list[dict[str, Any]] = []
        if decision["decision"] == "use":
            store = KnowledgeBaseStore()
            for doc_id in decision.get("document_ids") or []:
                found = store.get(doc_id)
                if found:
                    prior_docs.append(found)
            logger.info("loaded prior docs: %s", [d.get("id") for d in prior_docs])

        analysis = analyze_pdf(text, prior_documents=prior_docs, llm=self.llm)
        result["analysis"] = analysis

        if self.auto_ingest:
            result["ingest"] = ingest(path, store="knowledge_base")
            logger.info("ingest: %s", result["ingest"].get("document_id"))

        logger.info("agent done: status=%s", result["status"])
        return result
