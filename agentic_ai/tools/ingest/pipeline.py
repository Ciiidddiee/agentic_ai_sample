"""Ingest pipeline: raw → processed → store index."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from agentic_ai.environment.stores.config import load_store_config
from agentic_ai.environment.stores.knowledge_base import KnowledgeBaseStore
from agentic_ai.paths import ensure_data_dirs
from agentic_ai.tools.ocr.tool import run_ocr


def ingest(
    document_path: Path,
    store: str = "knowledge_base",
    document_id: str | None = None,
) -> dict[str, Any]:
    """Run OCR/normalize, then index into the store.

    Returns document_id and stage paths.
    """
    path = Path(document_path)
    if not path.is_file():
        raise FileNotFoundError(f"Document not found: {path}")

    dirs = ensure_data_dirs()
    doc_id = document_id or f"doc_{uuid.uuid4().hex[:12]}"

    ocr = run_ocr(path)
    text = ocr["text"]
    if not text.strip():
        raise ValueError(f"No extractable text in {path}")

    processed_dir = dirs["processed"] / doc_id
    processed_dir.mkdir(parents=True, exist_ok=True)
    text_path = processed_dir / "text.txt"
    meta_path = processed_dir / "meta.json"
    text_path.write_text(text, encoding="utf-8")
    meta = {
        "document_id": doc_id,
        "source": str(path),
        "filename": path.name,
        "confidence": ocr["confidence"],
        "page_count": len(ocr["pages"]),
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    config = load_store_config(store)
    kb = KnowledgeBaseStore(config)
    kb.index(
        doc_id,
        {
            "text": text,
            "source": str(path),
            "metadata": {
                "filename": path.name,
                "source": str(path),
                "confidence": ocr["confidence"],
            },
        },
    )

    return {
        "document_id": doc_id,
        "processed_path": str(processed_dir),
        "text_path": str(text_path),
        "confidence": ocr["confidence"],
        "store": store,
    }
