from pathlib import Path

import pytest

from agentic_ai.environment.stores.config import StoreConfig
from agentic_ai.environment.stores.knowledge_base import KnowledgeBaseStore
from agentic_ai.tools.ingest import ingest
from agentic_ai.tools.search import search

SAMPLES = Path(__file__).resolve().parents[2] / "data" / "raw" / "samples"


@pytest.fixture()
def isolated_kb(tmp_path, monkeypatch):
    kb_path = tmp_path / "knowledge_base"
    data_root = tmp_path / "data"
    (data_root / "processed").mkdir(parents=True)
    monkeypatch.setenv("DATA_DIR", str(data_root))

    config = StoreConfig(
        name="knowledge_base",
        path=kb_path,
        collection="documents",
        embedding_model="chroma-default",
    )
    return config


def test_ingest_and_search_ranks_invoice_above_contract(isolated_kb, monkeypatch):
    store = KnowledgeBaseStore(isolated_kb)

    def _kb(config=None):
        return KnowledgeBaseStore(isolated_kb)

    monkeypatch.setattr(
        "agentic_ai.tools.ingest.pipeline.KnowledgeBaseStore",
        lambda config=None: store,
    )
    monkeypatch.setattr(
        "agentic_ai.tools.search.tool.KnowledgeBaseStore",
        lambda config=None: store,
    )
    monkeypatch.setattr(
        "agentic_ai.tools.search.tool.load_store_config",
        lambda name=None: isolated_kb,
    )
    monkeypatch.setattr(
        "agentic_ai.tools.ingest.pipeline.load_store_config",
        lambda name=None: isolated_kb,
    )

    for name in (
        "invoice_acme_2024_q1.pdf",
        "invoice_acme_2024_q2.pdf",
        "contract_beta_services.pdf",
    ):
        pdf = SAMPLES / name
        assert pdf.is_file()
        ingest(pdf, document_id=f"sample_{pdf.stem}")

    hits = search("Acme Corp SaaS invoice Total Due payment terms Net 30", top_k=3)
    assert hits
    assert "invoice" in hits[0]["id"]
    assert "contract" not in hits[0]["id"]
