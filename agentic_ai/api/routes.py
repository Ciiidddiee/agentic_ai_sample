"""API routes for upload, ingest, search, and defect analysis."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile

from agentic_ai.agents.defect_analyzer import DefectAnalyzer
from agentic_ai.agents.defect_analyzer.skills.decide_prior_context.run import (
    ASK_OPTIONS,
)
from agentic_ai.shared.environment.uploads import save_upload

_SUPPORTED = {".pdf", ".xlsx", ".xlsm", ".xltx", ".xltm"}


def _ensure_supported(filename: str) -> None:
    suffix = Path(filename).suffix.lower()
    if suffix not in _SUPPORTED:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Use PDF or Excel (.xlsx).",
        )


def register_routes(app: FastAPI) -> None:
    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/ingest")
    async def ingest_upload(file: UploadFile = File(...)) -> dict[str, Any]:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Missing filename")
        _ensure_supported(file.filename)
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")
        path = save_upload(content=content, filename=file.filename)
        try:
            result = DefectAnalyzer().ingest(path)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"path": str(path), **result}

    @app.post("/v1/analyze")
    async def analyze_upload(
        file: UploadFile = File(...),
        user_action: str | None = Form(None),
        document_ids: str | None = Form(
            None,
            description="Comma-separated prior doc ids when user_action=use",
        ),
    ) -> dict[str, Any]:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Missing filename")
        _ensure_supported(file.filename)
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")
        path = save_upload(content=content, filename=file.filename)
        action = (user_action or "").strip().lower() or None
        if action is not None and action not in ASK_OPTIONS:
            raise HTTPException(
                status_code=400,
                detail=f"user_action must be one of {list(ASK_OPTIONS)}",
            )
        ids = (
            [p.strip() for p in document_ids.split(",") if p.strip()]
            if document_ids
            else None
        )
        try:
            return DefectAnalyzer().run(
                path,
                user_action=action,  # type: ignore[arg-type]
                document_ids=ids,
            )
        except Exception as exc:  # noqa: BLE001 — surface to client for MVP
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.get("/v1/search")
    def search_kb(
        q: str = Query(..., min_length=1),
        top_k: int = Query(5, ge=1, le=20),
    ) -> dict[str, Any]:
        hits = DefectAnalyzer().search(q, top_k=top_k)
        return {"query": q, "hits": hits}
