"""Example: run DefectAnalyzer on a sample upload."""

from pathlib import Path

from agentic_ai.agents.defect_analyzer import DefectAnalyzer
from agentic_ai.shared.logging_setup import setup_logging


def main() -> None:
    setup_logging()
    document = Path("data/raw/samples/invoice_acme_2024_q2.pdf")
    if not document.is_file():
        raise SystemExit("Run: python scripts/generate_sample_pdfs.py")
    agent = DefectAnalyzer()
    result = agent.run(document)
    print(result)


if __name__ == "__main__":
    main()
