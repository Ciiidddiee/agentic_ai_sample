"""FastAPI application entrypoint."""

from __future__ import annotations

from dotenv import load_dotenv
from fastapi import FastAPI

from agentic_ai.api.routes import register_routes
from agentic_ai.logging_setup import setup_logging
from agentic_ai.paths import ensure_data_dirs

load_dotenv()
setup_logging()
ensure_data_dirs()

app = FastAPI(
    title="Agentic AI PDF Analyst",
    version="0.1.0",
    description="Upload PDFs to ingest, search, and analyze with prior context.",
)
register_routes(app)
