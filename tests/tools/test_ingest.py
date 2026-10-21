from pathlib import Path

from agentic_ai.agents.defect_analyzer.skills.ingest.run import ingest_defect
from agentic_ai.shared.environment.stores.config import StoreConfig
from agentic_ai.shared.environment.stores.knowledge_base import KnowledgeBaseStore

SAMPLES = Path(__file__).resolve().parents[2] / "data" / "raw" / "samples"


def test_ingest_writes_processed_and_indexes(tmp_path, monkeypatch):
    data_root = tmp_path / "data"
    kb_path = tmp_path / "kb"
    monkeypatch.setenv("DATA_DIR", str(data_root))
    config = StoreConfig(
        name="knowledge_base",
        path=kb_path,
        collection="documents",
        embedding_model="chroma-default",
    )
    store = KnowledgeBaseStore(config)
    monkeypatch.setattr(
        "agentic_ai.agents.defect_analyzer.skills.ingest.run.KnowledgeBaseStore",
        lambda cfg=None: store,
    )

    pdf = SAMPLES / "invoice_acme_2024_q1.pdf"
    result = ingest_defect(pdf, document_id="test_defect_q1", store=store)
    assert result["document_id"] == "test_defect_q1"
    assert result["kind"] == "defect"
    assert Path(result["text_path"]).is_file()
    assert store.get("test_defect_q1") is not None
