"""Generate a sample Excel workbook for DefectAnalyzer demos."""

from __future__ import annotations

import sys
from pathlib import Path

from openpyxl import Workbook

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT = PROJECT_ROOT / "data" / "raw" / "samples" / "sales_acme_2024_q1.xlsx"


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = "Sales"
    ws.append(["Product", "Qty", "Unit Price", "Total", "Period"])
    ws.append(["Cloud hosting", 1, 8000, 8000, "2024-Q1"])
    ws.append(["Support retainer", 1, 2400, 2400, "2024-Q1"])
    ws.append(["API usage", 1, 2000, 2000, "2024-Q1"])
    notes = wb.create_sheet("Notes")
    notes.append(["Customer", "Contoso Ltd"])
    notes.append(["Terms", "Net 30"])
    notes.append(["Related", "Acme Corp SaaS invoice Q1"])
    wb.save(OUT)
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
