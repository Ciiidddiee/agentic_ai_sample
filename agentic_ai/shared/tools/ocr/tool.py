"""Shared PDF OCR extractor (format plumbing for any agent)."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def run_ocr(document_path: Path) -> dict[str, Any]:
    """Extract text from a PDF via pdfplumber.

    Returns: text, confidence, kind, pages, blocks, page_count
    """
    import pdfplumber

    path = Path(document_path)
    if not path.is_file():
        raise FileNotFoundError(f"Document not found: {path}")

    pages_out: list[dict[str, Any]] = []
    blocks: list[dict[str, Any]] = []
    texts: list[str] = []

    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text() or ""
            texts.append(page_text)
            pages_out.append({"page": i + 1, "text": page_text})
            if page_text.strip():
                blocks.append({"page": i + 1, "type": "text", "text": page_text})

    full_text = "\n\n".join(texts).strip()
    n_pages = max(len(pages_out), 1)
    n_with_text = sum(1 for p in pages_out if p["text"].strip())
    confidence = n_with_text / n_pages if full_text else 0.0

    return {
        "text": full_text,
        "confidence": confidence,
        "kind": "pdf",
        "pages": pages_out,
        "blocks": blocks,
        "page_count": len(pages_out),
    }
