from pathlib import Path

from agentic_ai.environment.stores.config import StoreConfig
from agentic_ai.environment.stores.knowledge_base import KnowledgeBaseStore
from agentic_ai.tools.ingest import ingest

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
        "agentic_ai.tools.ingest.pipeline.KnowledgeBaseStore",
        lambda cfg=None: store,
    )
    monkeypatch.setattr(
        "agentic_ai.tools.ingest.pipeline.load_store_config",
        lambda name=None: config,
    )

    pdf = SAMPLES / "invoice_acme_2024_q1.pdf"
    result = ingest(pdf, document_id="test_inv_q1")
    assert result["document_id"] == "test_inv_q1"
    assert Path(result["text_path"]).is_file()
    assert store.get("test_inv_q1") is not None
