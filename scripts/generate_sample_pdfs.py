"""Generate sample PDFs for ingest / similarity demos."""

from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "data" / "raw" / "samples"


def _write_pdf(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    y = height - 72
    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, y, lines[0])
    y -= 28
    c.setFont("Helvetica", 11)
    for line in lines[1:]:
        if y < 72:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = height - 72
        c.drawString(72, y, line)
        y -= 16
    c.save()


def main() -> int:
    samples = {
        "invoice_acme_2024_q1.pdf": [
            "INVOICE — Acme Corp",
            "Invoice Number: INV-ACME-2024-Q1",
            "Bill To: Contoso Ltd",
            "Period: January–March 2024",
            "Line items: Cloud hosting, Support retainer, API usage",
            "Subtotal: $12,400.00",
            "Tax: $1,240.00",
            "Total Due: $13,640.00",
            "Payment terms: Net 30",
            "Notes: Standard Acme SaaS invoice for Q1 services.",
        ],
        "invoice_acme_2024_q2.pdf": [
            "INVOICE — Acme Corp",
            "Invoice Number: INV-ACME-2024-Q2",
            "Bill To: Contoso Ltd",
            "Period: April–June 2024",
            "Line items: Cloud hosting, Support retainer, API usage, Extra storage",
            "Subtotal: $13,100.00",
            "Tax: $1,310.00",
            "Total Due: $14,410.00",
            "Payment terms: Net 30",
            "Notes: Standard Acme SaaS invoice for Q2 services. Similar to Q1.",
        ],
        "contract_beta_services.pdf": [
            "MASTER SERVICES AGREEMENT — Beta Labs",
            "Agreement ID: MSA-BETA-7781",
            "Parties: Beta Labs and Northwind Traders",
            "Scope: Custom software development and on-site consulting",
            "Term: 24 months commencing 1 May 2024",
            "Fees: Time and materials at agreed hourly rates",
            "Confidentiality: Mutual NDA incorporated by reference",
            "Termination: Either party may terminate with 60 days notice",
            "Governing law: State of Delaware",
            "Notes: This is a services contract, not an invoice.",
        ],
    }

    for name, lines in samples.items():
        out = OUT_DIR / name
        _write_pdf(out, lines)
        print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
