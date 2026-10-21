from pathlib import Path

from agentic_ai.agents.defect_analyzer import DefectAnalyzer
from agentic_ai.shared.environment.stores.config import StoreConfig
from agentic_ai.shared.environment.stores.knowledge_base import KnowledgeBaseStore

SAMPLES = Path(__file__).resolve().parents[2] / "data" / "raw" / "samples"


class FakeLLM:
    def __init__(self) -> None:
        self.n = 0

    def chat(self, messages, response_format=None, label: str = "chat"):
        self.n += 1
        if self.n == 1:
            return (
                '{"decision":"use","document_ids":["sample_invoice_acme_2024_q1"],'
                '"reason":"Matching prior Acme case"}'
            )
        return (
            '{"summary":"Q2 Acme report similar to Q1",'
            '"findings":["Same customer Contoso","Net 30 terms"],'
            '"severity":"medium",'
            '"citations":["sample_invoice_acme_2024_q1"]}'
        )


def _patch_store(monkeypatch, store):
    monkeypatch.setattr(
        "agentic_ai.agents.defect_analyzer.skills.ingest.run.KnowledgeBaseStore",
        lambda cfg=None: store,
    )
    monkeypatch.setattr(
        "agentic_ai.agents.defect_analyzer.skills.search.run.KnowledgeBaseStore",
        lambda cfg=None: store,
    )
    monkeypatch.setattr(
        "agentic_ai.agents.defect_analyzer.agent.KnowledgeBaseStore",
        lambda cfg=None: store,
    )


def test_use_analyzes_without_ingest(tmp_path, monkeypatch):
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
    _patch_store(monkeypatch, store)

    q1 = SAMPLES / "invoice_acme_2024_q1.pdf"
    q2 = SAMPLES / "invoice_acme_2024_q2.pdf"
    DefectAnalyzer().ingest(q1, document_id="sample_invoice_acme_2024_q1", store=store)

    agent = DefectAnalyzer(llm=FakeLLM())  # type: ignore[arg-type]
    result = agent.run(q2)
    assert result["agent"] == "defect_analyzer"
    assert result["status"] == "ok"
    assert result["decision"]["decision"] == "use"
    assert result["analysis"]["summary"]
    assert result["ingest"] is None


def test_ask_then_continue_analyzes_without_ingest(tmp_path, monkeypatch):
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
    _patch_store(monkeypatch, store)

    class AskThenAnalyze:
        def chat(self, messages, response_format=None, label: str = "chat"):
            if label == "decide_prior_context":
                return (
                    '{"decision":"ask","document_ids":[],'
                    '"reason":"Unclear match"}'
                )
            return (
                '{"summary":"Acme Q1 sales sheet",'
                '"findings":["Cloud hosting is largest line"],'
                '"severity":"low",'
                '"citations":[]}'
            )

    xlsx = SAMPLES / "sales_acme_2024_q1.xlsx"
    assert xlsx.is_file()
    DefectAnalyzer().ingest(
        SAMPLES / "invoice_acme_2024_q1.pdf",
        document_id="sample_invoice_acme_2024_q1",
        store=store,
    )

    agent = DefectAnalyzer(llm=AskThenAnalyze())  # type: ignore[arg-type]
    first = agent.run(xlsx)
    assert first["status"] == "needs_input"
    assert "continue" in first["options"]

    second = agent.run(xlsx, user_action="continue")
    assert second["status"] == "ok"
    assert second["decision"]["resolved_as"] == "continue"
    assert second["analysis"]["summary"]
    assert second["ingest"] is None


def test_ask_then_ingest_only(tmp_path, monkeypatch):
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
    _patch_store(monkeypatch, store)

    agent = DefectAnalyzer()
    pdf = SAMPLES / "invoice_acme_2024_q1.pdf"
    first = agent.run(pdf)
    assert first["status"] == "needs_input"

    second = agent.run(pdf, user_action="ingest")
    assert second["status"] == "ingested"
    assert second["analysis"] is None
    assert second["ingest"]["kind"] == "defect"
    assert second["ingest"]["document_id"]


def test_ask_then_drop(tmp_path, monkeypatch):
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
    _patch_store(monkeypatch, store)

    agent = DefectAnalyzer()
    pdf = SAMPLES / "invoice_acme_2024_q1.pdf"
    first = agent.run(pdf)
    assert first["status"] == "needs_input"

    second = agent.run(pdf, user_action="drop")
    assert second["status"] == "dropped"
    assert second["analysis"] is None
    assert second["ingest"] is None
