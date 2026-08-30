"""
Single swap point for LLM providers. Every service depends on
`get_llm_provider()` (via FastAPI Depends or direct call) — never on a
concrete provider class. Changing `LLM_PROVIDER` in settings/.env is the
only change needed to move from mock -> OpenAI -> Gemini.
"""
from app.ai_core.llm.base import LLMProvider
from app.core.config import get_settings


def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    provider = settings.LLM_PROVIDER.lower().split("#")[0].strip()

    if provider == "openai":
        from app.ai_core.llm.openai_provider import OpenAIProvider
        return OpenAIProvider()
    if provider == "gemini":
        from app.ai_core.llm.gemini_provider import GeminiProvider
        return GeminiProvider()

    if settings.ENVIRONMENT != "local":
        raise ValueError(f"Invalid or missing LLM_PROVIDER in production: '{settings.LLM_PROVIDER}'")

    from app.ai_core.llm.mock_provider import MockLLMProvider
    return MockLLMProvider()
