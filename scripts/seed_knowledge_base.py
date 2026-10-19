"""Ingest sample PDFs into the knowledge base."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_ai.paths import ensure_data_dirs
from agentic_ai.tools.ingest.pipeline import ingest

SAMPLES = PROJECT_ROOT / "data" / "raw" / "samples"


def main() -> int:
    ensure_data_dirs()
    if not SAMPLES.is_dir():
        print(f"No samples at {SAMPLES}. Run scripts/generate_sample_pdfs.py first.")
        return 1

    pdfs = sorted(SAMPLES.glob("*.pdf"))
    if not pdfs:
        print("No PDF samples found.")
        return 1

    for pdf in pdfs:
        # Stable ids from filename stem for easier debugging
        doc_id = f"sample_{pdf.stem}"
        result = ingest(pdf, store="knowledge_base", document_id=doc_id)
        print(f"Ingested {pdf.name} -> {result['document_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
