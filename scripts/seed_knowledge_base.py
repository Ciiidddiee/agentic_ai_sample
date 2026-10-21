"""Ingest sample documents as defect cases into the knowledge base."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_ai.agents.defect_analyzer import DefectAnalyzer
from agentic_ai.shared.paths import ensure_data_dirs

SAMPLES = PROJECT_ROOT / "data" / "raw" / "samples"


def main() -> int:
    ensure_data_dirs()
    if not SAMPLES.is_dir():
        print(f"No samples at {SAMPLES}. Run scripts/generate_sample_pdfs.py first.")
        return 1

    files = sorted(SAMPLES.glob("*.pdf")) + sorted(SAMPLES.glob("*.xlsx"))
    if not files:
        print("No sample PDF/Excel files found.")
        return 1

    agent = DefectAnalyzer()
    for path in files:
        doc_id = f"sample_{path.stem}"
        result = agent.ingest(path, document_id=doc_id)
        print(f"Ingested {path.name} -> {result['document_id']} ({result['kind']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
