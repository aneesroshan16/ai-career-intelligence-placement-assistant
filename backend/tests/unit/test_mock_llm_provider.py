import pytest
from pydantic import BaseModel

from app.ai_core.llm.base import LLMMessage
from app.ai_core.llm.mock_provider import MockLLMProvider


class _DummySuggestion(BaseModel):
    issue: str
    severity: str


class _DummySchema(BaseModel):
    score: float
    tips: list[str]
    suggestions: list[_DummySuggestion]


@pytest.mark.asyncio
async def test_complete_returns_deterministic_text():
    provider = MockLLMProvider()
    messages = [LLMMessage(role="user", content="hello world")]
    r1 = await provider.complete(messages)
    r2 = await provider.complete(messages)
    assert r1.content == r2.content
    assert r1.model == "mock-llm-v1"


@pytest.mark.asyncio
async def test_complete_json_fills_nested_schema():
    provider = MockLLMProvider()
    messages = [LLMMessage(role="user", content="generate suggestions")]
    result = await provider.complete_json(messages, _DummySchema)

    assert isinstance(result, _DummySchema)
    assert isinstance(result.score, float)
    assert isinstance(result.tips, list) and len(result.tips) >= 2
    assert isinstance(result.suggestions, list) and len(result.suggestions) >= 2
    assert isinstance(result.suggestions[0], _DummySuggestion)


@pytest.mark.asyncio
async def test_complete_json_is_deterministic_for_same_input():
    provider = MockLLMProvider()
    messages = [LLMMessage(role="user", content="same input twice")]
    r1 = await provider.complete_json(messages, _DummySchema)
    r2 = await provider.complete_json(messages, _DummySchema)
    assert r1.model_dump() == r2.model_dump()
