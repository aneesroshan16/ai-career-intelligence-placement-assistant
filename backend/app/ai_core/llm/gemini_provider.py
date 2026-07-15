"""
Real Google Gemini implementation of LLMProvider. Inactive until
settings.LLM_PROVIDER is set to "gemini" and GEMINI_API_KEY is configured.
"""
from __future__ import annotations

import json
from typing import TypeVar

from pydantic import BaseModel

from app.ai_core.llm.base import LLMMessage, LLMProvider, LLMResponse
from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError

TModel = TypeVar("TModel", bound=BaseModel)


class GeminiProvider(LLMProvider):
    def __init__(self):
        settings = get_settings()
        if not settings.GEMINI_API_KEY:
            raise ExternalServiceError("GEMINI_API_KEY is not configured")
        import google.generativeai as genai  # lazy import

        genai.configure(api_key=settings.GEMINI_API_KEY)
        self._genai = genai
        self._model_name = settings.GEMINI_MODEL

    @staticmethod
    def _flatten(messages: list[LLMMessage]) -> str:
        return "\n\n".join(f"[{m.role.upper()}]\n{m.content}" for m in messages)

    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        try:
            model = self._genai.GenerativeModel(self._model_name)
            resp = await model.generate_content_async(
                self._flatten(messages),
                generation_config={"temperature": temperature, "max_output_tokens": max_tokens},
            )
            return LLMResponse(content=resp.text, model=self._model_name)
        except Exception as exc:  # noqa: BLE001
            raise ExternalServiceError(f"Gemini completion failed: {exc}") from exc

    async def complete_json(self, messages: list[LLMMessage], schema: type[TModel]) -> TModel:
        try:
            model = self._genai.GenerativeModel(self._model_name)
            prompt = self._flatten(messages) + (
                f"\n\nRespond ONLY with valid JSON matching this schema:\n"
                f"{json.dumps(schema.model_json_schema())}"
            )
            resp = await model.generate_content_async(
                prompt, generation_config={"response_mime_type": "application/json"},
            )
            return schema.model_validate_json(resp.text)
        except Exception as exc:  # noqa: BLE001
            raise ExternalServiceError(f"Gemini structured completion failed: {exc}") from exc
