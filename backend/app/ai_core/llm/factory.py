"""
Single swap point for LLM providers. Every service depends on
`get_llm_provider()` (via FastAPI Depends or direct call) — never on a
concrete provider class. Changing `LLM_PROVIDER` in settings/.env is the
only change needed to move from mock -> OpenAI -> Gemini.
"""
from functools import lru_cache

from app.ai_core.llm.base import LLMProvider
from app.core.config import get_settings


@lru_cache
def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    provider = settings.LLM_PROVIDER.lower()

    if provider == "openai":
        from app.ai_core.llm.openai_provider import OpenAIProvider
        return OpenAIProvider()
    if provider == "gemini":
        from app.ai_core.llm.gemini_provider import GeminiProvider
        return GeminiProvider()

    from app.ai_core.llm.mock_provider import MockLLMProvider
    return MockLLMProvider()
