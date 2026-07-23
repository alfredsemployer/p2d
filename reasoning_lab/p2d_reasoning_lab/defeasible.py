"""Deterministic grounded-semantics checks for defeasible argument records."""

from __future__ import annotations

from typing import Any


QUALIFYING_ARGUMENT_ASSESSMENTS = {"moderate", "strong", "decisive"}
ACTIVE_DEFEATER_STATES = {"supported", "accepted"}


def evaluate_defeasible_graph(graph: dict[str, Any]) -> dict[str, Any]:
    """Compute a conservative argument status without asking an LLM.

    This is deliberately a policy engine, not a truth oracle. A qualifying
    argument is defeated when a supported defeater targets it and that
    defeater has at least one positively valent claim premise.
    """

    claims = {
        str(item.get("id")): item for item in graph.get("claims") or []
    }
    defeaters_by_target: dict[str, list[dict[str, Any]]] = {}
    for defeater in graph.get("defeaters") or []:
        defeaters_by_target.setdefault(
            str(defeater.get("target_id") or ""), []
        ).append(defeater)

    argument_results: list[dict[str, Any]] = []
    accepted_conclusions: set[str] = set()
    for argument in graph.get("arguments") or []:
        argument_id = str(argument.get("id") or "")
        qualifying = str(argument.get("assessment") or "") in (
            QUALIFYING_ARGUMENT_ASSESSMENTS
        )
        active_defeaters: list[str] = []
        unresolved_defeaters: list[str] = []
        for defeater in defeaters_by_target.get(argument_id, []):
            premise_ids = list(defeater.get("premise_claim_ids") or [])
            premise_positive = any(
                (
                    claims.get(premise_id, {})
                    .get("epistemic_assessment", {})
                    .get("valence", 0.0)
                    > 0.0
                )
                for premise_id in premise_ids
            )
            status = str(defeater.get("status") or "unresolved")
            if status in ACTIVE_DEFEATER_STATES and premise_positive:
                active_defeaters.append(str(defeater.get("id") or ""))
            elif status in {"contested", "unresolved"}:
                unresolved_defeaters.append(str(defeater.get("id") or ""))
        if not qualifying:
            dialectical_status = "rejected"
            reason = "argument strength is below the policy floor"
        elif active_defeaters:
            dialectical_status = "rejected"
            reason = "a supported, claim-backed defeater is active"
        elif unresolved_defeaters:
            dialectical_status = "undecided"
            reason = "an unresolved defeater remains"
        else:
            dialectical_status = "accepted"
            reason = "argument qualifies and has no active defeater"
            accepted_conclusions.add(str(argument.get("conclusion_claim_id")))
        argument_results.append(
            {
                "argument_id": argument_id,
                "dialectical_status": dialectical_status,
                "reason": reason,
                "active_defeater_ids": active_defeaters,
                "unresolved_defeater_ids": unresolved_defeaters,
            }
        )

    claim_results = [
        {
            "claim_id": claim_id,
            "has_accepted_argument": claim_id in accepted_conclusions,
            "epistemic_valence_sign": (
                claim.get("epistemic_assessment", {}).get(
                    "valence_sign", "unassessed"
                )
            ),
        }
        for claim_id, claim in sorted(claims.items())
    ]
    return {
        "engine": "grounded-defeasible-policy-v1",
        "semantic_limit": (
            "This establishes policy-governed dialectical acceptance, not "
            "world truth and not probability."
        ),
        "arguments": argument_results,
        "claims": claim_results,
    }
