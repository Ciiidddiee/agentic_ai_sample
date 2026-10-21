"""Ingest a defect report into the shared store."""

from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path
from typing import Any

from agentic_ai.shared.environment.stores.knowledge_base import KnowledgeBaseStore
from agentic_ai.shared.paths import ensure_data_dirs
from agentic_ai.shared.tools.extract import extract_document

logger = logging.getLogger(__name__)


def ingest_defect(
    document_path: Path,
    *,
    document_id: str | None = None,
    store: KnowledgeBaseStore | None = None,
    extracted: dict[str, Any] | None = None,
) -> dict[str, Any]:
    path = Path(document_path)
    dirs = ensure_data_dirs()
    doc_id = document_id or f"defect_{uuid.uuid4().hex[:12]}"

    result = extracted or extract_document(path)
    body = str(result.get("text") or "")
    if not body.strip():
        raise ValueError(f"No extractable text in {path}")

    processed_dir = dirs["processed"] / doc_id
    processed_dir.mkdir(parents=True, exist_ok=True)
    text_path = processed_dir / "text.txt"
    meta_path = processed_dir / "meta.json"
    text_path.write_text(body, encoding="utf-8")

    source_kind = str(result.get("kind") or "unknown")
    confidence = float(result.get("confidence") or 0.0)
    meta: dict[str, Any] = {
        "document_id": doc_id,
        "source": str(path),
        "filename": path.name,
        "confidence": confidence,
        "source_kind": source_kind,
        "kind": "defect",
    }
    if "page_count" in result:
        meta["page_count"] = result["page_count"]
    if "sheet_count" in result:
        meta["sheet_count"] = result["sheet_count"]
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    kb = store or KnowledgeBaseStore()
    kb.index(
        doc_id,
        {
            "text": body,
            "source": str(path),
            "metadata": {
                "filename": path.name,
                "source": str(path),
                "confidence": confidence,
                "kind": "defect",
                "source_kind": source_kind,
            },
        },
    )
    logger.info("defect ingest: %s (source_kind=%s)", doc_id, source_kind)
    return {
        "document_id": doc_id,
        "processed_path": str(processed_dir),
        "text_path": str(text_path),
        "confidence": confidence,
        "kind": "defect",
        "source_kind": source_kind,
    }
