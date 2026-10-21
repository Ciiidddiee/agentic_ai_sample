from pathlib import Path

import yaml

from agentic_ai.shared.llm.config import LLMConfig, load_llm_config


def test_public_groq_model_id(tmp_path):
    path = tmp_path / "model.yaml"
    path.write_text(
        yaml.dump(
            {
                "provider": "groq",
                "model": "llama-3.3-70b-versatile",
                "temperature": 0.1,
            }
        ),
        encoding="utf-8",
    )
    cfg = load_llm_config(path)
    assert cfg.resolve_model_id() == "groq/llama-3.3-70b-versatile"
    kwargs = cfg.litellm_kwargs()
    assert kwargs["model"] == "groq/llama-3.3-70b-versatile"
    assert "api_base" not in kwargs


def test_internal_openai_compatible_sets_api_base(tmp_path, monkeypatch):
    monkeypatch.setenv("INTERNAL_LLM_API_KEY", "secret-key")
    path = tmp_path / "model.yaml"
    path.write_text(
        yaml.dump(
            {
                "provider": "openai_compatible",
                "model": "company-chat-v1",
                "base_url": "http://llm.internal.company:8000/v1",
                "api_key_env": "INTERNAL_LLM_API_KEY",
            }
        ),
        encoding="utf-8",
    )
    cfg = load_llm_config(path)
    assert cfg.resolve_model_id() == "openai/company-chat-v1"
    kwargs = cfg.litellm_kwargs()
    assert kwargs["api_base"] == "http://llm.internal.company:8000/v1"
    assert kwargs["api_key"] == "secret-key"


def test_model_id_override(tmp_path):
    cfg = LLMConfig(
        provider="groq",
        model="ignored",
        model_id="gemini/gemini-2.0-flash",
    )
    assert cfg.resolve_model_id() == "gemini/gemini-2.0-flash"


def test_openai_compatible_requires_base_url():
    cfg = LLMConfig(provider="openai_compatible", model="x")
    try:
        cfg.litellm_kwargs()
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "base_url" in str(exc)
