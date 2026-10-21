from pathlib import Path

import pytest

from agentic_ai.agents.defect_analyzer.skills.ingest.run import ingest_defect
from agentic_ai.agents.defect_analyzer.skills.search.run import search_prior_defects
from agentic_ai.shared.environment.stores.config import StoreConfig
from agentic_ai.shared.environment.stores.knowledge_base import KnowledgeBaseStore

SAMPLES = Path(__file__).resolve().parents[2] / "data" / "raw" / "samples"


@pytest.fixture()
def isolated_kb(tmp_path, monkeypatch):
    kb_path = tmp_path / "knowledge_base"
    data_root = tmp_path / "data"
    (data_root / "processed").mkdir(parents=True)
    monkeypatch.setenv("DATA_DIR", str(data_root))

    return StoreConfig(
        name="knowledge_base",
        path=kb_path,
        collection="documents",
        embedding_model="chroma-default",
    )


def test_ingest_and_search_ranks_invoice_above_contract(isolated_kb, monkeypatch):
    store = KnowledgeBaseStore(isolated_kb)

    monkeypatch.setattr(
        "agentic_ai.agents.defect_analyzer.skills.ingest.run.KnowledgeBaseStore",
        lambda config=None: store,
    )
    monkeypatch.setattr(
        "agentic_ai.agents.defect_analyzer.skills.search.run.KnowledgeBaseStore",
        lambda config=None: store,
    )

    for name in (
        "invoice_acme_2024_q1.pdf",
        "invoice_acme_2024_q2.pdf",
        "contract_beta_services.pdf",
    ):
        pdf = SAMPLES / name
        assert pdf.is_file()
        ingest_defect(pdf, document_id=f"sample_{pdf.stem}", store=store)

    hits = search_prior_defects(
        "Acme Corp SaaS invoice Total Due payment terms Net 30",
        top_k=3,
        store=store,
    )
    assert hits
    assert "invoice" in hits[0]["id"]
    assert "contract" not in hits[0]["id"]
