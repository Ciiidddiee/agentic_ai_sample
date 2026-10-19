from pathlib import Path

from agentic_ai.tools.ocr import run_ocr

SAMPLES = Path(__file__).resolve().parents[2] / "data" / "raw" / "samples"


def test_run_ocr_on_sample_invoice():
    pdf = SAMPLES / "invoice_acme_2024_q1.pdf"
    assert pdf.is_file(), "Run scripts/generate_sample_pdfs.py first"
    result = run_ocr(pdf)
    assert "Acme" in result["text"]
    assert result["confidence"] > 0
    assert result["pages"]
