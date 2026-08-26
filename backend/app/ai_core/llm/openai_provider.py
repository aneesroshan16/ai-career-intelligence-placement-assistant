"""
Real OpenAI implementation of LLMProvider. Inactive until settings.LLM_PROVIDER
is set to "openai" and OPENAI_API_KEY is configured — see ai_core/llm/factory.py.

Uses the Chat Completions API with `response_format={"type": "json_schema", ...}`
for `complete_json`, mapping the Pydantic schema to a JSON schema so responses
are structurally validated by the API itself before we even parse them.
"""
from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel

from app.ai_core.llm.base import LLMMessage, LLMProvider, LLMResponse
from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError

TModel = TypeVar("TModel", bound=BaseModel)


class OpenAIProvider(LLMProvider):
    def __init__(self):
        settings = get_settings()
        if not settings.OPENAI_API_KEY:
            raise ExternalServiceError("OPENAI_API_KEY is not configured")
        # Lazy import so the `openai` package is only required when this provider is active.
        from openai import AsyncOpenAI

        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY, timeout=25.0)
        self._model = settings.OPENAI_MODEL

    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        try:
            resp = await self._client.chat.completions.create(
                model=self._model,
                messages=[m.model_dump() for m in messages],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            choice = resp.choices[0]
            return LLMResponse(
                content=choice.message.content or "",
                model=resp.model,
                usage=resp.usage.model_dump() if resp.usage else None,
            )
        except Exception as exc:  # noqa: BLE001 — external API, deliberately broad
            raise ExternalServiceError(f"OpenAI completion failed: {exc}") from exc

    async def complete_json(self, messages: list[LLMMessage], schema: type[TModel]) -> TModel:
        # 1. Try modern Structured Outputs parse method first
        try:
            response = await self._client.beta.chat.completions.parse(
                model=self._model,
                messages=[m.model_dump() for m in messages],
                response_format=schema,
            )
            parsed = response.choices[0].message.parsed
            if parsed is not None:
                return parsed
        except Exception:
            pass

        # 2. Fallback to json_object mode with Pydantic validation
        try:
            json_messages = [m.model_dump() for m in messages]
            if json_messages and json_messages[0].get("role") == "system":
                json_messages[0]["content"] = (
                    f"{json_messages[0]['content']}\n"
                    f"Respond with valid JSON matching this schema: {schema.model_json_schema()}"
                )
            resp = await self._client.chat.completions.create(
                model=self._model,
                messages=json_messages,
                response_format={"type": "json_object"},
            )
            raw = resp.choices[0].message.content or "{}"
            return schema.model_validate_json(raw)
        except Exception as exc:  # noqa: BLE001
            raise ExternalServiceError(f"OpenAI structured completion failed: {exc}") from exc

