"""Tests for decide_prior_context with a fake LLM."""

from pathlib import Path

from agentic_ai.agents.defect_analyzer.skills.decide_prior_context.run import (
    ASK_OPTIONS,
    decide_prior_context,
)


class FakeLLM:
    def __init__(self, content: str) -> None:
        self.content = content
        self.calls = 0

    def chat(self, messages, response_format=None, label: str = "chat"):
        self.calls += 1
        return self.content


def test_empty_hits_ask_without_llm():
    result = decide_prior_context([])
    assert result["decision"] == "ask"
    assert result["document_ids"] == []
    assert result["options"] == list(ASK_OPTIONS)


def test_very_low_score_ask_without_llm():
    result = decide_prior_context(
        [{"id": "doc_1", "score": 0.2, "snippet": "weak"}],
        document_text="unrelated",
        min_score=0.75,
    )
    assert result["decision"] == "ask"
    assert "options" in result


def test_llm_use_decision():
    llm = FakeLLM(
        '{"decision":"use","document_ids":["doc_1"],"reason":"Strong match"}'
    )
    result = decide_prior_context(
        [{"id": "doc_1", "score": 0.9, "snippet": "weld crack"}],
        document_text="weld crack report",
        llm=llm,  # type: ignore[arg-type]
        min_score=0.75,
    )
    assert result["decision"] == "use"
    assert result["document_ids"] == ["doc_1"]
    assert llm.calls == 1


def test_llm_skip_mapped_to_ask():
    llm = FakeLLM(
        '{"decision":"skip","document_ids":[],"reason":"Not related"}'
    )
    result = decide_prior_context(
        [{"id": "doc_1", "score": 0.8, "snippet": "maybe"}],
        document_text="report",
        llm=llm,  # type: ignore[arg-type]
        min_score=0.75,
    )
    assert result["decision"] == "ask"
    assert result["options"] == list(ASK_OPTIONS)


def test_examples_file_exists():
    path = (
        Path(__file__).resolve().parents[2]
        / "agentic_ai"
        / "agents"
        / "defect_analyzer"
        / "skills"
        / "decide_prior_context"
        / "examples.jsonl"
    )
    assert path.is_file()
