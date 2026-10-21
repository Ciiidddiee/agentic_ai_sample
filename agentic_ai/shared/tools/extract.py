"""Route a file to the shared PDF or Excel extractor."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentic_ai.shared.tools.ocr.tool import run_ocr
from agentic_ai.shared.tools.read_excel.tool import read_excel

_PDF = {".pdf"}
_EXCEL = {".xlsx", ".xlsm", ".xltx", ".xltm"}


def extract_document(document_path: Path) -> dict[str, Any]:
    """Pick OCR or read_excel from the file suffix."""
    path = Path(document_path)
    suffix = path.suffix.lower()
    if suffix in _PDF:
        return run_ocr(path)
    if suffix in _EXCEL:
        return read_excel(path)
    raise ValueError(
        f"Unsupported file type '{suffix}'. Use PDF or Excel (.xlsx)."
    )
