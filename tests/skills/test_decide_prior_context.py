"""Tests for decide_prior_context with a fake LLM."""

from pathlib import Path

from agentic_ai.skills.decide_prior_context.run import decide_prior_context


class FakeLLM:
    def __init__(self, content: str) -> None:
        self.content = content
        self.calls = 0

    def chat(self, messages, response_format=None, label: str = "chat"):
        self.calls += 1
        return self.content


def test_empty_hits_skip_without_llm():
    result = decide_prior_context([])
    assert result["decision"] == "skip"
    assert result["document_ids"] == []


def test_llm_use_decision():
    llm = FakeLLM(
        '{"decision":"use","document_ids":["doc_1"],"reason":"Strong match"}'
    )
    result = decide_prior_context(
        [{"id": "doc_1", "score": 0.9, "snippet": "invoice"}],
        document_text="invoice text",
        llm=llm,  # type: ignore[arg-type]
        min_score=0.75,
    )
    assert result["decision"] == "use"
    assert result["document_ids"] == ["doc_1"]
    assert llm.calls == 1


def test_examples_file_exists():
    path = (
        Path(__file__).resolve().parents[2]
        / "agentic_ai"
        / "skills"
        / "decide_prior_context"
        / "examples.jsonl"
    )
    assert path.is_file()
