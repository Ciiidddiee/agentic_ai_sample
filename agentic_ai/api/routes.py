"""API routes for upload, ingest, search, and analysis."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, File, HTTPException, Query, UploadFile

from agentic_ai.agents.pdf_analyst import PdfAnalystAgent
from agentic_ai.environment.uploads import save_upload
from agentic_ai.tools.ingest.pipeline import ingest
from agentic_ai.tools.search.tool import search


def register_routes(app: FastAPI) -> None:
    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/ingest")
    async def ingest_upload(file: UploadFile = File(...)) -> dict[str, Any]:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Missing filename")
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")
        path = save_upload(content=content, filename=file.filename)
        try:
            result = ingest(path, store="knowledge_base")
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"path": str(path), **result}

    @app.post("/v1/analyze")
    async def analyze_upload(file: UploadFile = File(...)) -> dict[str, Any]:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Missing filename")
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")
        path = save_upload(content=content, filename=file.filename)
        agent = PdfAnalystAgent()
        try:
            return agent.run(path)
        except Exception as exc:  # noqa: BLE001 — surface to client for MVP
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.get("/v1/search")
    def search_kb(
        q: str = Query(..., min_length=1),
        top_k: int = Query(5, ge=1, le=20),
    ) -> dict[str, Any]:
        hits = search(q, store="knowledge_base", top_k=top_k)
        return {"query": q, "hits": hits}
