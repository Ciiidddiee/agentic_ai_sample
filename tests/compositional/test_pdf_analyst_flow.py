from pathlib import Path

from agentic_ai.agents.pdf_analyst import PdfAnalystAgent
from agentic_ai.environment.stores.config import StoreConfig
from agentic_ai.environment.stores.knowledge_base import KnowledgeBaseStore
from agentic_ai.tools.ingest import ingest

SAMPLES = Path(__file__).resolve().parents[2] / "data" / "raw" / "samples"


class FakeLLM:
    def __init__(self) -> None:
        self.n = 0

    def chat(self, messages, response_format=None, label: str = "chat"):
        self.n += 1
        if self.n == 1:
            return (
                '{"decision":"use","document_ids":["sample_invoice_acme_2024_q1"],'
                '"reason":"Matching Acme invoice"}'
            )
        return (
            '{"summary":"Q2 Acme invoice similar to Q1",'
            '"findings":["Same customer Contoso","Net 30 terms"],'
            '"citations":["sample_invoice_acme_2024_q1"]}'
        )


def test_agent_flow_with_fake_llm(tmp_path, monkeypatch):
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
    monkeypatch.setattr(
        "agentic_ai.tools.search.tool.KnowledgeBaseStore",
        lambda cfg=None: store,
    )
    monkeypatch.setattr(
        "agentic_ai.tools.search.tool.load_store_config",
        lambda name=None: config,
    )
    monkeypatch.setattr(
        "agentic_ai.agents.pdf_analyst.agent.KnowledgeBaseStore",
        lambda cfg=None: store,
    )

    q1 = SAMPLES / "invoice_acme_2024_q1.pdf"
    q2 = SAMPLES / "invoice_acme_2024_q2.pdf"
    ingest(q1, document_id="sample_invoice_acme_2024_q1")

    agent = PdfAnalystAgent(llm=FakeLLM(), auto_ingest=True)  # type: ignore[arg-type]
    result = agent.run(q2)
    assert result["status"] == "ok"
    assert result["decision"]["decision"] == "use"
    assert result["analysis"]["summary"]
    assert result["ingest"]["document_id"]
