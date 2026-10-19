"""Example: ingest a document into the default store."""

from pathlib import Path

from agentic_ai.tools.ingest import ingest


def main() -> None:
    document = Path("data/raw/samples/invoice_acme_2024_q1.pdf")
    if not document.is_file():
        raise SystemExit("Run: python scripts/generate_sample_pdfs.py")
    result = ingest(document, store="knowledge_base")
    print(result)


if __name__ == "__main__":
    main()
