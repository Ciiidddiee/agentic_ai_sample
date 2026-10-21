"""Example: ingest a document as a defect case."""

from pathlib import Path

from agentic_ai.agents.defect_analyzer import DefectAnalyzer


def main() -> None:
    document = Path("data/raw/samples/invoice_acme_2024_q1.pdf")
    if not document.is_file():
        raise SystemExit("Run: python scripts/generate_sample_pdfs.py")
    result = DefectAnalyzer().ingest(document)
    print(result)


if __name__ == "__main__":
    main()
