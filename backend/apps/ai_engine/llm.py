"""Shared generative-LLM helpers.

The project's primary generative model is Google Gemini (a cheap "flash" model
by default). Ollama-served models remain as automatic fallback. Call sites pass
a model name; :func:`is_gemini_model` decides which backend handles it.

Uses the Gemini REST API directly via ``httpx`` (already a dependency) so no
extra SDK is required.
"""

from __future__ import annotations

import json
from typing import Any

import httpx
from django.conf import settings


class GeminiError(ValueError):
    """Raised when the Gemini API cannot return a usable completion.

    Subclasses ``ValueError`` so call sites that iterate over candidate models
    (catching ``ValueError`` to fall through to the next model) treat a
    misconfigured/unavailable Gemini as "try the next model", not a task crash.
    """


def is_gemini_model(model: str | None) -> bool:
    return str(model or "").strip().lower().startswith("gemini")


def gemini_generate_text(
    prompt: str,
    model: str,
    *,
    temperature: float = 0.0,
    max_output_tokens: int | None = None,
) -> tuple[str, dict[str, Any]]:
    """Call Gemini ``generateContent`` and return ``(text, token_usage)``.

    ``responseMimeType`` is set to ``application/json`` so the returned text is a
    JSON document, matching how the Ollama call sites use ``format="json"``.
    """
    api_key = getattr(settings, "GEMINI_API_KEY", "")
    if not api_key:
        raise GeminiError("GEMINI_API_KEY (GOOGLE_GEMINI_API) is not configured.")

    base_url = getattr(
        settings, "GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta"
    ).rstrip("/")
    max_tokens = max_output_tokens or getattr(settings, "GEMINI_MAX_OUTPUT_TOKENS", 8192)

    generation_config: dict[str, Any] = {
        "temperature": temperature,
        "responseMimeType": "application/json",
        "maxOutputTokens": max_tokens,
    }
    thinking_budget = getattr(settings, "GEMINI_THINKING_BUDGET", 0)
    if thinking_budget is not None and int(thinking_budget) >= 0:
        generation_config["thinkingConfig"] = {"thinkingBudget": int(thinking_budget)}

    response = httpx.post(
        f"{base_url}/models/{model}:generateContent",
        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
        json={
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": generation_config,
        },
        timeout=getattr(settings, "GEMINI_TIMEOUT_SECONDS", 120),
    )
    response.raise_for_status()
    body = response.json()

    candidates = body.get("candidates") or []
    if not candidates:
        feedback = body.get("promptFeedback")
        raise ValueError(f"Gemini '{model}' returned no candidates (feedback={feedback!r}).")

    candidate = candidates[0]
    parts = (candidate.get("content") or {}).get("parts") or []
    text = "".join(part.get("text", "") for part in parts).strip()
    if not text:
        raise ValueError(
            f"Gemini '{model}' returned empty text "
            f"(finishReason={candidate.get('finishReason')!r})."
        )

    usage = body.get("usageMetadata") or {}
    token_usage = {
        "prompt_eval_count": usage.get("promptTokenCount"),
        "eval_count": usage.get("candidatesTokenCount"),
        "total_tokens": usage.get("totalTokenCount"),
    }
    return text, {key: value for key, value in token_usage.items() if value is not None}


def gemini_generate_json(
    prompt: str,
    model: str,
    *,
    temperature: float = 0.0,
    max_output_tokens: int | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Like :func:`gemini_generate_text` but returns the parsed JSON object."""
    text, usage = gemini_generate_text(
        prompt,
        model,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )
    return json.loads(text), usage
