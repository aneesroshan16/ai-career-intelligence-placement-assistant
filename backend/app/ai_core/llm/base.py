"""
Abstract LLM provider interface. All AI-dependent services (ATS suggestions,
roadmap generation, interview feedback, coding problem generation) code
against this interface only — never against a concrete provider — so
swapping mock -> OpenAI -> Gemini is a config change, not a refactor.
"""
from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

TModel = TypeVar("TModel", bound=BaseModel)


class LLMMessage(BaseModel):
    role: str  # "system" | "user" | "assistant"
    content: str


class LLMResponse(BaseModel):
    content: str
    model: str
    usage: dict | None = None


class LLMProvider(ABC):
    """Contract every concrete LLM provider (mock/openai/gemini) must satisfy."""

    @abstractmethod
    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """Free-form text completion."""
        raise NotImplementedError

    @abstractmethod
    async def complete_json(self, messages: list[LLMMessage], schema: type[TModel]) -> TModel:
        """
        Structured generation: returns a validated instance of `schema`.
        Used for roadmap plans, interview questions/feedback, ATS suggestions,
        and coding problem generation — anywhere the caller needs a typed object,
        not free text.
        """
        raise NotImplementedError
