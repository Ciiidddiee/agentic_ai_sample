"""Accept uploads and place them under data/raw."""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from agentic_ai.paths import ensure_data_dirs


def save_upload(
    source: Path | None = None,
    *,
    content: bytes | None = None,
    filename: str | None = None,
    raw_dir: Path | None = None,
) -> Path:
    """Copy bytes or a file into the raw data directory. Returns stored path."""
    dirs = ensure_data_dirs()
    dest_dir = raw_dir or dirs["raw"]
    dest_dir.mkdir(parents=True, exist_ok=True)

    if content is not None:
        name = filename or f"upload_{uuid.uuid4().hex}.pdf"
        dest = dest_dir / name
        dest.write_bytes(content)
        return dest

    if source is None:
        raise ValueError("Provide source path or content bytes")

    source = Path(source)
    suffix = source.suffix or ".pdf"
    dest_name = filename or f"{source.stem}_{uuid.uuid4().hex[:8]}{suffix}"
    dest = dest_dir / dest_name
    shutil.copy2(source, dest)
    return dest
