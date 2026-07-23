"""Governed, append-only records for inspecting and challenging an artifact."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any, Literal


InteractionKind = Literal["challenge", "deepen", "explain", "trust_preference"]


def make_interaction_record(
    *,
    kind: InteractionKind,
    artifact_id: str,
    target_id: str,
    request: str,
    actor: str = "user",
    created_at: str | None = None,
) -> dict[str, Any]:
    if not artifact_id or not target_id or not request.strip():
        raise ValueError("artifact_id, target_id, and request are required")
    timestamp = created_at or datetime.now(UTC).isoformat()
    identity = json.dumps(
        [kind, artifact_id, target_id, request, actor, timestamp],
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return {
        "id": "IX-" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16],
        "kind": kind,
        "artifact_id": artifact_id,
        "target_id": target_id,
        "request": request,
        "actor": actor,
        "created_at": timestamp,
        "status": "proposed",
        "mutation_policy": (
            "The interaction may propose a new artifact version; it never "
            "silently changes an existing verdict."
        ),
    }


def validate_interaction_transition(
    before: dict[str, Any], after: dict[str, Any]
) -> None:
    allowed = {
        "proposed": {"running", "rejected"},
        "running": {"completed", "failed"},
        "completed": set(),
        "failed": set(),
        "rejected": set(),
    }
    old = str(before.get("status"))
    new = str(after.get("status"))
    if new not in allowed.get(old, set()):
        raise ValueError(f"invalid interaction transition: {old} -> {new}")
