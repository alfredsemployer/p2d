"""Deterministic projection from the reasoning artifact to visual cards."""

from __future__ import annotations

from typing import Any


def card_designation(
    claim_id: str,
    *,
    terminal_ids: set[str],
    defeater_premise_ids: set[str],
) -> str:
    if claim_id in terminal_ids:
        return "answer"
    if claim_id in defeater_premise_ids:
        return "challenge"
    return "support"


def build_visual_projection(graph: dict[str, Any]) -> dict[str, Any]:
    terminal_ids = {
        claim_id
        for ids in (graph.get("terminal_claim_ids_by_question") or {}).values()
        for claim_id in ids
    }
    defeater_premise_ids = {
        claim_id
        for defeater in graph.get("defeaters") or []
        for claim_id in defeater.get("premise_claim_ids") or []
    }
    cards: list[dict[str, Any]] = []
    for claim in graph.get("claims") or []:
        claim_id = str(claim["id"])
        epistemic = dict(claim.get("epistemic_assessment") or {})
        coverage = dict(claim.get("coverage_record") or {})
        depth = dict(claim.get("evidence_depth") or {})
        cards.append(
            {
                "claim_id": claim_id,
                "text": claim.get("proposition", ""),
                "designation": card_designation(
                    claim_id,
                    terminal_ids=terminal_ids,
                    defeater_premise_ids=defeater_premise_ids,
                ),
                "valence": epistemic.get("valence"),
                "valence_sign": epistemic.get("valence_sign"),
                "direction_label": epistemic.get("forced_binary_direction"),
                "coverage_state": coverage.get("coverage_state"),
                "coverage_harvey_quarters": coverage.get("harvey_quarters"),
                "evidence_depth": depth,
                "source_fields": {
                    "designation": "topology",
                    "valence": "claim.epistemic_assessment",
                    "coverage": "claim.coverage_record",
                    "evidence_depth": "claim.evidence_depth",
                },
            }
        )
    return {
        "projection_version": "visual-card-v1",
        "cards": cards,
        "arguments": [
            {
                "argument_id": item.get("id"),
                "premise_claim_ids": item.get("premise_claim_ids") or [],
                "conclusion_claim_id": item.get("conclusion_claim_id"),
                "relationship": "supports",
            }
            for item in graph.get("arguments") or []
            if item.get("premise_claim_ids")
        ],
        "defeaters": [
            {
                "defeater_id": item.get("id"),
                "premise_claim_ids": item.get("premise_claim_ids") or [],
                "target_argument_id": item.get("target_id"),
                "relationship": item.get("attack_type"),
            }
            for item in graph.get("defeaters") or []
        ],
        "layout_constraints": {
            "terminal_side": "left",
            "flow": "right_to_left",
            "edges": "orthogonal",
            "node_overlap": "forbidden",
            "equal_width_within_section": True,
        },
    }
