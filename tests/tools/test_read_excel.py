from pathlib import Path

from agentic_ai.shared.tools.read_excel import read_excel

SAMPLES = Path(__file__).resolve().parents[2] / "data" / "raw" / "samples"


def test_read_excel_sample():
    path = SAMPLES / "sales_acme_2024_q1.xlsx"
    assert path.is_file(), "Run scripts/generate_sample_excel.py first"
    result = read_excel(path)
    assert "Cloud hosting" in result["text"]
    assert result["confidence"] == 1.0
    assert len(result["sheets"]) >= 1
    assert result["kind"] == "excel"
