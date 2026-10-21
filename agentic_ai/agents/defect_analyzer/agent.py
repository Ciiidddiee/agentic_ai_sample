"""DefectAnalyzer: perceive → decide → act for defect reports (PDF or Excel)."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Literal

from agentic_ai.agents.defect_analyzer.skills.analyze_defect.run import analyze_defect
from agentic_ai.agents.defect_analyzer.skills.decide_prior_context.run import (
    ASK_OPTIONS,
    decide_prior_context,
)
from agentic_ai.agents.defect_analyzer.skills.ingest.run import ingest_defect
from agentic_ai.agents.defect_analyzer.skills.search.run import search_prior_defects
from agentic_ai.shared.environment.stores.knowledge_base import KnowledgeBaseStore
from agentic_ai.shared.llm.client import LLMClient
from agentic_ai.shared.tools.extract import extract_document

logger = logging.getLogger(__name__)

UserAction = Literal["continue", "ingest", "drop", "use"]


class DefectAnalyzer:
    """Upload → extract → search → use|ask → analyze and/or ingest.

    Ingest only happens when a human chooses ``user_action="ingest"`` under ask
    (or via ``.ingest()`` / ``POST /v1/ingest``). The ``use`` path analyzes only.
    """

    def __init__(
        self,
        llm: LLMClient | None = None,
        *,
        top_k: int = 5,
    ) -> None:
        self.llm = llm
        self.top_k = top_k

    def ingest(
        self,
        document_path: Path,
        *,
        document_id: str | None = None,
        store: KnowledgeBaseStore | None = None,
    ) -> dict[str, Any]:
        """Index a defect report (PDF or Excel) into the shared KB."""
        return ingest_defect(
            Path(document_path),
            document_id=document_id,
            store=store,
        )

    def search(
        self,
        query: str,
        *,
        top_k: int | None = None,
        store: KnowledgeBaseStore | None = None,
    ) -> list[dict[str, Any]]:
        """Search prior defect cases."""
        return search_prior_defects(
            query,
            top_k=top_k or self.top_k,
            store=store,
        )

    def run(
        self,
        document_path: Path,
        *,
        user_action: UserAction | None = None,
        document_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """Run the flow, or resume after ``needs_input`` with ``user_action``.

        After ``ask``, pass one of: continue | ingest | drop | use.
        Only ``ingest`` writes to the KB from this loop.
        """
        path = Path(document_path)
        logger.info(
            "DefectAnalyzer start: %s user_action=%s",
            path,
            user_action,
        )

        extracted = extract_document(path)
        text = str(extracted.get("text") or "")
        source_kind = str(extracted.get("kind") or "unknown")
        confidence = float(extracted.get("confidence") or 0.0)
        logger.info(
            "perception/extract: kind=%s confidence=%.2f chars=%s",
            source_kind,
            confidence,
            len(text),
        )

        hits = search_prior_defects(text, top_k=self.top_k)
        logger.info(
            "perception/search: %s hit(s) %s",
            len(hits),
            [(h.get("id"), round(float(h.get("score", 0)), 3)) for h in hits],
        )

        extract_meta: dict[str, Any] = {
            "confidence": confidence,
            "source_kind": source_kind,
        }
        if source_kind == "pdf":
            extract_meta["page_count"] = int(extracted.get("page_count") or 0)
        else:
            extract_meta["sheet_count"] = int(extracted.get("sheet_count") or 0)

        result: dict[str, Any] = {
            "document_path": str(path),
            "extract": extract_meta,
            "hits": hits,
            "decision": None,
            "user_action": user_action,
            "analysis": None,
            "ingest": None,
            "status": "ok",
            "agent": "defect_analyzer",
        }

        if user_action is None:
            decision = decide_prior_context(
                hits,
                document_text=text,
                llm=self.llm,
            )
            result["decision"] = decision
            logger.info("decision: %s", decision)

            if decision["decision"] == "ask":
                result["status"] = "needs_input"
                result["options"] = decision.get("options") or list(ASK_OPTIONS)
                logger.info(
                    "DefectAnalyzer stop: needs_input options=%s",
                    result["options"],
                )
                return result

            # use → analyze with priors only (no ingest)
            return self._finish_analyze(
                result,
                text=text,
                prior_ids=list(decision.get("document_ids") or []),
            )

        action = str(user_action).lower()
        if action not in ASK_OPTIONS:
            result["status"] = "error"
            result["decision"] = {
                "decision": "ask",
                "reason": f"Invalid user_action {user_action!r}",
                "options": list(ASK_OPTIONS),
            }
            return result

        result["decision"] = {
            "decision": "ask",
            "resolved_as": action,
            "document_ids": list(document_ids or []),
            "reason": f"Human chose {action}",
            "options": list(ASK_OPTIONS),
        }

        if action == "drop":
            result["status"] = "dropped"
            logger.info("DefectAnalyzer dropped by user")
            return result

        if action == "ingest":
            result["ingest"] = ingest_defect(path, extracted=extracted)
            result["status"] = "ingested"
            logger.info(
                "DefectAnalyzer ingest-only: %s",
                result["ingest"].get("document_id"),
            )
            return result

        prior_ids: list[str] = []
        if action == "use":
            prior_ids = list(document_ids or [])
            if not prior_ids and hits:
                prior_ids = [str(hits[0]["id"])]
            result["decision"]["document_ids"] = prior_ids

        # continue / use → analyze only (no ingest)
        return self._finish_analyze(result, text=text, prior_ids=prior_ids)

    def _finish_analyze(
        self,
        result: dict[str, Any],
        *,
        text: str,
        prior_ids: list[str],
    ) -> dict[str, Any]:
        prior_docs: list[dict[str, Any]] = []
        if prior_ids:
            store = KnowledgeBaseStore()
            for doc_id in prior_ids:
                found = store.get(doc_id)
                if found:
                    prior_docs.append(found)
            logger.info("loaded prior docs: %s", [d.get("id") for d in prior_docs])

        result["analysis"] = analyze_defect(
            text, prior_documents=prior_docs, llm=self.llm
        )
        result["status"] = "ok"
        logger.info("DefectAnalyzer done: status=%s (no auto-ingest)", result["status"])
        return result
