"""Strict-enough JSON extraction for heterogeneous model responses."""

from __future__ import annotations

import json
import re
from typing import Any

from json_repair import repair_json


def parse_json_object(text: str) -> dict[str, Any]:
    candidate = (text or "").strip()
    if candidate.startswith("```"):
        candidate = re.sub(r"^```(?:json)?\s*", "", candidate, count=1)
        candidate = candidate.rsplit("```", 1)[0].strip()
    try:
        value = json.loads(candidate)
    except json.JSONDecodeError:
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start < 0:
            raise ValueError("model response contains no JSON object") from None
        fragment = candidate[start:] if end < start else candidate[start : end + 1]
        try:
            value = json.loads(fragment)
        except json.JSONDecodeError:
            value = json.loads(repair_json(fragment))
    if not isinstance(value, dict):
        raise ValueError("expected a JSON object")
    return value
