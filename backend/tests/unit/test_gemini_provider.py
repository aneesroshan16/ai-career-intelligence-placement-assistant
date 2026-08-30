import pytest
from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError
from app.ai_core.llm.factory import get_llm_provider
from app.ai_core.llm.gemini_provider import GeminiProvider
from app.ai_core.llm.openai_provider import OpenAIProvider
from app.ai_core.llm.mock_provider import MockLLMProvider


def test_factory_selects_mock_by_default(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    get_settings.cache_clear()
    provider = get_llm_provider()
    assert isinstance(provider, MockLLMProvider)


def test_factory_selects_gemini_and_fails_if_key_missing(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "")
    get_settings.cache_clear()
    with pytest.raises(ExternalServiceError, match="GEMINI_API_KEY is not configured"):
        get_llm_provider()


def test_factory_selects_gemini_when_configured(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "dummy_gemini_key_for_test")
    get_settings.cache_clear()
    provider = get_llm_provider()
    assert isinstance(provider, GeminiProvider)


def test_factory_preserves_openai_selection(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy_openai_key_for_test")
    get_settings.cache_clear()
    provider = get_llm_provider()
    assert isinstance(provider, OpenAIProvider)
