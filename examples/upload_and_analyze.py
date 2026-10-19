"""Example: run the PDF analyst flow on a local sample file.

Requires GROQ_API_KEY (or another configured LLM) in .env for live calls.
For a dry structural check without LLM, prefer pytest instead.
"""

from pathlib import Path

from agentic_ai.agents.pdf_analyst import PdfAnalystAgent


def main() -> None:
    document = Path("data/raw/samples/invoice_acme_2024_q2.pdf")
    if not document.is_file():
        raise SystemExit("Run: python scripts/generate_sample_pdfs.py")
    agent = PdfAnalystAgent()
    result = agent.run(document)
    print(result)


if __name__ == "__main__":
    main()
