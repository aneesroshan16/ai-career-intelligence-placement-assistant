"""
MockLLMProvider — deterministic, zero-cost, zero-dependency stand-in for a
real LLM. It satisfies the exact same `LLMProvider` interface as the real
OpenAI/Gemini providers, so every service in the codebase (roadmap, ATS,
interview, coding) can be developed, tested, and demoed end-to-end before
a real API key is ever configured.

Determinism: responses are seeded from a hash of the input messages, so the
same input always produces the same output (useful for tests and demos).

Structured generation (`complete_json`) introspects the target Pydantic
schema and fills it with plausible, type-appropriate values using simple
field-name heuristics — no hardcoding per-module schema is required here,
which keeps this provider fully decoupled from the modules that use it.
"""
from __future__ import annotations

import hashlib
import random
import typing
from typing import TypeVar, get_args, get_origin

from pydantic import BaseModel

from app.ai_core.llm.base import LLMMessage, LLMProvider, LLMResponse

TModel = TypeVar("TModel", bound=BaseModel)

_CANNED_TIPS = [
    "Use the STAR method to structure your answer with a concrete example.",
    "Quantify your impact with numbers wherever possible.",
    "Slow down and structure your answer before diving into details.",
    "Tie your answer back to the specific role you're targeting.",
    "Practice a concise 60-90 second version of this answer.",
]

_CANNED_SUGGESTIONS = [
    "Add measurable outcomes (%, numbers, scale) to your project bullets.",
    "Include a dedicated 'Skills' section with role-relevant keywords.",
    "Use consistent, ATS-friendly section headers (Experience, Education, Skills).",
    "Avoid embedding text inside images or tables — ATS parsers may skip it.",
    "Move your most relevant project to the top of the section.",
]


def _seed_from_messages(messages: list[LLMMessage]) -> int:
    joined = "|".join(m.content for m in messages)
    return int(hashlib.sha256(joined.encode()).hexdigest(), 16) % (2**32)


def _mock_value_for_field(field_name: str, annotation, rng: random.Random):
    origin = get_origin(annotation)
    args = get_args(annotation)

    # Optional[...] / Union[..., None]
    if origin is typing.Union and type(None) in args:
        non_none = [a for a in args if a is not type(None)]
        return _mock_value_for_field(field_name, non_none[0], rng) if non_none else None

    if origin in (list, typing.List):
        inner = args[0] if args else str
        count = rng.randint(2, 4)
        return [_mock_value_for_field(field_name, inner, rng) for _ in range(count)]

    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return _fill_schema(annotation, rng).model_dump()

    if annotation is bool:
        return rng.random() > 0.5

    if annotation is int:
        low, high = (1, 10)
        if "score" in field_name or "percentage" in field_name:
            low, high = (60, 95)
        if "week" in field_name or "hour" in field_name:
            low, high = (1, 12)
        return rng.randint(low, high)

    if annotation is float:
        if "score" in field_name or "percentage" in field_name or "probability" in field_name:
            return round(rng.uniform(0.55, 0.92), 2)
        return round(rng.uniform(1.0, 10.0), 2)

    # str and fallback
    name = field_name.lower()
    if "tip" in name:
        return rng.choice(_CANNED_TIPS)
    if "suggestion" in name or "recommendation" in name:
        return rng.choice(_CANNED_SUGGESTIONS)
    if "question" in name:
        return "Tell me about a challenging project you worked on and how you approached it."
    if "feedback" in name or "answer" in name or "content" in name:
        return "Solid structure overall — strengthen this with a specific, quantified example."
    if "skill" in name:
        return rng.choice(["Python", "SQL", "Machine Learning", "React", "Docker", "System Design"])
    if "title" in name or "focus" in name:
        return "Core skill-building module"
    if "task" in name or "deliverable" in name or "goal" in name:
        return "Complete a hands-on mini-project applying this week's concepts."
    return f"mock_{field_name}"


def _fill_schema(schema: type[TModel], rng: random.Random) -> TModel:
    values = {}
    for field_name, field in schema.model_fields.items():
        values[field_name] = _mock_value_for_field(field_name, field.annotation, rng)
    return schema(**values)


class MockLLMProvider(LLMProvider):
    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        seed = _seed_from_messages(messages)
        rng = random.Random(seed)
        last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
        snippet = last_user[:80].replace("\n", " ")
        text = (
            f"[mock-llm response] Based on your input (\"{snippet}...\"), here is a "
            f"structured, actionable response. This is a deterministic placeholder — "
            f"swap LLM_PROVIDER=openai|gemini in settings to use a real model."
        )
        return LLMResponse(content=text, model="mock-llm-v1", usage={"prompt_tokens": len(last_user.split())})

    async def complete_json(self, messages: list[LLMMessage], schema: type[TModel]) -> TModel:
        seed = _seed_from_messages(messages)
        rng = random.Random(seed)
        return _fill_schema(schema, rng)
