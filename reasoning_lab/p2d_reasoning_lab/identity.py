"""Stable claim identity without pretending that paraphrase detection is solved."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from typing import Any


_SPACE = re.compile(r"\s+")


def normalize_text(value: str) -> str:
    """Normalize superficial variation while preserving propositional content."""

    value = unicodedata.normalize("NFKC", value).strip().casefold()
    value = value.replace("“", '"').replace("”", '"').replace("’", "'")
    return _SPACE.sub(" ", value)


def claim_identity_payload(claim: dict[str, Any]) -> dict[str, Any]:
    """Return the fields that define a claim's scoped proposition."""

    return {
        "proposition": normalize_text(str(claim.get("proposition") or "")),
        "polarity": normalize_text(str(claim.get("polarity") or "positive")),
        "modality": normalize_text(str(claim.get("modality") or "")),
        "conditions": sorted(
            normalize_text(str(item)) for item in claim.get("conditions") or []
        ),
        "temporal_scope": normalize_text(str(claim.get("temporal_scope") or "")),
        "comparison_class": normalize_text(
            str(claim.get("comparison_class") or "")
        ),
        "operationalization": normalize_text(
            str(claim.get("operationalization") or "")
        ),
    }


def claim_fingerprint(claim: dict[str, Any], *, length: int = 20) -> str:
    """Return a deterministic content fingerprint for versioned claim identity."""

    payload = json.dumps(
        claim_identity_payload(claim),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:length]


def attach_claim_identity(claim: dict[str, Any]) -> dict[str, Any]:
    """Copy a claim and add stable identity metadata."""

    result = dict(claim)
    result.setdefault("version", 1)
    result["claim_uid"] = f"claim:{claim_fingerprint(result)}"
    result["identity_policy"] = "scoped-proposition-sha256-v1"
    return result


def exact_correspondence(left: dict[str, Any], right: dict[str, Any]) -> bool:
    """Conservatively merge only claims with identical normalized scope."""

    return claim_identity_payload(left) == claim_identity_payload(right)
