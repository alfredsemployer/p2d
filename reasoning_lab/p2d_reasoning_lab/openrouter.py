"""Small OpenRouter client with mandatory cost accounting."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .budget import BudgetLedger
from .jsonutil import parse_json_object


API_URL = "https://openrouter.ai/api/v1/chat/completions"

# USD per token. Values are a run-time planning aid; provider-reported
# ``usage.cost`` is authoritative in the ledger.
MODEL_PRICING = {
    "openai/gpt-5.6-luna": (0.000001, 0.000006),
    "google/gemini-2.5-pro": (0.00000125, 0.000010),
    "deepseek/deepseek-v3.2": (0.000000269, 0.0000004),
    "nvidia/nemotron-3-super-120b-a12b": (0.00000008, 0.00000045),
}


def load_api_key(key_file: str | Path | None = None) -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key and key_file is not None:
        key = Path(key_file).read_text(encoding="utf-8").strip()
    if not key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is unset and no external --key-file was supplied"
        )
    return key


@dataclass(slots=True)
class ModelReply:
    content: str
    response_id: str
    model: str
    usage: dict[str, Any]


class OpenRouterClient:
    def __init__(self, api_key: str, ledger: BudgetLedger) -> None:
        self._api_key = api_key
        self.ledger = ledger

    @staticmethod
    def estimate_reservation(
        model: str, prompt: str, max_tokens: int, *, web: bool
    ) -> float:
        prompt_price, output_price = MODEL_PRICING[model]
        estimated_prompt_tokens = max(1, len(prompt) // 3)
        token_cost = (
            estimated_prompt_tokens * prompt_price + max_tokens * output_price
        )
        # Three low-context web results cost much less in ordinary use. This
        # large reservation protects the hard run ceiling from injected text.
        web_reserve = 0.25 if web else 0.0
        return max(0.01, token_cost * 1.35 + web_reserve)

    def call(
        self,
        *,
        purpose: str,
        model: str,
        prompt: str,
        max_tokens: int = 1600,
        temperature: float = 0.1,
        web: bool = False,
        json_mode: bool = False,
    ) -> ModelReply:
        reservation = self.ledger.reserve(
            purpose=purpose,
            model=model,
            amount_usd=self.estimate_reservation(
                model, prompt, max_tokens, web=web
            ),
        )
        body: dict[str, Any] = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        if web:
            body["plugins"] = [{"id": "web", "max_results": 3}]
            body["web_search_options"] = {"search_context_size": "low"}
        if model == "google/gemini-2.5-pro":
            body["reasoning"] = {"effort": "low", "exclude": True}

        request = urllib.request.Request(
            API_URL,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://p2d.space",
                "X-Title": "p2d reasoning lab",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                payload = json.load(response)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"OpenRouter HTTP {exc.code} for {purpose}: {detail[:500]}"
            ) from exc

        usage = dict(payload.get("usage") or {})
        actual_cost = usage.get("cost")
        if actual_cost is None:
            prompt_tokens = int(usage.get("prompt_tokens") or 0)
            completion_tokens = int(usage.get("completion_tokens") or 0)
            prompt_price, output_price = MODEL_PRICING[model]
            actual_cost = (
                prompt_tokens * prompt_price + completion_tokens * output_price
            )
        self.ledger.record(
            reservation,
            actual_cost_usd=float(actual_cost),
            response_id=str(payload.get("id") or ""),
            usage=usage,
        )
        message = payload["choices"][0]["message"]
        content = message.get("content") or message.get("reasoning") or ""
        return ModelReply(
            content=str(content),
            response_id=str(payload.get("id") or ""),
            model=str(payload.get("model") or model),
            usage=usage,
        )

    def call_json(self, **kwargs: Any) -> tuple[dict[str, Any], ModelReply]:
        # Some providers reject simultaneous web search and response_format.
        # The prompt still requests JSON, and malformed JSON is repaired locally.
        reply = self.call(json_mode=not bool(kwargs.get("web")), **kwargs)
        return parse_json_object(reply.content), reply
