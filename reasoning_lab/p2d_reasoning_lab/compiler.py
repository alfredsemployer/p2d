"""Compile a native reasoning artifact into one governed, visualizable graph."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

from .coverage import build_coverage_record, build_evidence_depth_record
from .defeasible import evaluate_defeasible_graph
from .dependence import cluster_grounds, dependence_scenarios
from .formal import cross_check_propositional
from .identity import attach_claim_identity
from .projection import build_visual_projection
from .validation import (
    inferential_reachability_report,
    validate_graph_skeleton,
)
from .valuation import aggregate_valence, assessment_from_record


def _grounds_for_claim(
    claim_id: str,
    graph: dict[str, Any],
    ground_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    arguments_by_conclusion: dict[str, list[dict[str, Any]]] = {}
    for item in graph.get("arguments") or []:
        arguments_by_conclusion.setdefault(
            str(item.get("conclusion_claim_id") or ""), []
        ).append(item)

    ground_ids: set[str] = set()
    visited: set[str] = set()

    def collect(current_claim_id: str) -> None:
        if current_claim_id in visited:
            return
        visited.add(current_claim_id)
        for argument in arguments_by_conclusion.get(current_claim_id, []):
            ground_ids.update(argument.get("ground_ids") or [])
            for premise_id in argument.get("premise_claim_ids") or []:
                collect(str(premise_id))

    collect(claim_id)
    return [ground_by_id[item] for item in sorted(ground_ids) if item in ground_by_id]


def _research_lanes_for_claim(
    claim: dict[str, Any], research: dict[str, Any]
) -> list[dict[str, Any]]:
    direct = research.get(str(claim.get("id"))) or {}
    if direct:
        return list(direct.get("lanes") or [])
    lanes: list[dict[str, Any]] = []
    for source_id in claim.get("source_research_claim_ids") or []:
        lanes.extend((research.get(str(source_id)) or {}).get("lanes") or [])
    return lanes


def _formal_report(graph: dict[str, Any]) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    unsuitable = 0
    for argument in graph.get("arguments") or []:
        candidate = dict(argument.get("formal_candidate") or {})
        if not candidate.get("suitable"):
            unsuitable += 1
            continue
        result = cross_check_propositional(
            list(candidate.get("premises") or []),
            str(candidate.get("conclusion") or ""),
            formalization_fidelity=candidate.get(
                "fidelity", "candidate_unvalidated"
            ),
        )
        results.append(
            {
                "argument_id": argument.get("id"),
                "candidate": candidate,
                "result": result,
            }
        )
    return {
        "engine": "z3-plus-truth-table",
        "arguments_total": len(graph.get("arguments") or []),
        "formal_candidates_checked": len(results),
        "unsuitable_for_strict_formalization": unsuitable,
        "results": results,
        "semantic_limit": (
            "Solver results establish consequences of supplied formalizations "
            "only. They do not establish formalization fidelity or empirical truth."
        ),
    }


def compile_reasoning_artifact(
    *,
    graph: dict[str, Any],
    portfolio: dict[str, Any],
    research: dict[str, Any],
    grounds: list[dict[str, Any]],
    artifact_id: str,
) -> dict[str, Any]:
    """Validate and enrich a model-authored graph by deterministic policy."""

    compiled = deepcopy(graph)
    compiled["schema_version"] = "0.3.0"
    compiled["artifact_id"] = artifact_id
    compiled["compiled_at"] = datetime.now(UTC).isoformat()
    compiled["ontology_contract"] = {
        "card_vertices": "claims only",
        "arguments": "supporting inferential hyperedges, never cards",
        "defeaters": "attacking relations backed by claim premises, never cards",
        "grounds": "source-backed observations attached to arguments, never cards",
        "questions": "inquiry metadata and section headings, never cards",
        "sources": "provenance records for grounds, never cards",
    }

    ground_by_id = {str(item.get("id")): item for item in grounds}
    enriched_claims: list[dict[str, Any]] = []
    for raw_claim in compiled.get("claims") or []:
        claim = attach_claim_identity(raw_claim)
        records = list(claim.pop("valence_assessments", []) or [])
        if not records:
            raise ValueError(
                f"claim {claim.get('id')} has no explicit valence assessments"
            )
        claim["epistemic_assessment"] = aggregate_valence(
            [assessment_from_record(item) for item in records],
            prior_credence=float(claim.pop("prior_credence", 0.5)),
        )
        claim_grounds = _grounds_for_claim(
            str(claim.get("id")), compiled, ground_by_id
        )
        lanes = _research_lanes_for_claim(claim, research)
        claim["coverage_record"] = build_coverage_record(lanes)
        claim["evidence_depth"] = build_evidence_depth_record(claim_grounds)
        dependence = cluster_grounds(claim_grounds)
        dependence["sensitivity_scenarios"] = dependence_scenarios(dependence)
        claim["source_dependence"] = dependence
        enriched_claims.append(claim)
    compiled["claims"] = enriched_claims

    active_ids = {
        str(item.get("id"))
        for item in portfolio.get("questions") or []
        if item.get("disposition") == "active"
    }
    structural = validate_graph_skeleton(
        compiled,
        active_question_ids=active_ids,
        known_ground_ids=set(ground_by_id),
    )
    compiled["structural_validation"] = [item.to_dict() for item in structural]
    errors = [item for item in structural if item.severity == "error"]
    if errors:
        raise ValueError(
            "native graph failed validation: "
            + "; ".join(f"{item.code}: {item.message}" for item in errors)
        )

    compiled["inferential_reachability"] = inferential_reachability_report(
        compiled, active_question_ids=active_ids
    )
    compiled["defeasible_evaluation"] = evaluate_defeasible_graph(compiled)
    compiled["formal_validation"] = _formal_report(compiled)
    compiled["visual_projection"] = build_visual_projection(compiled)
    compiled["interaction_contract"] = {
        "record_types": ["challenge", "deepen", "explain", "trust_preference"],
        "mutation_policy": (
            "Interactions append records and may create a new artifact version; "
            "they never silently mutate this artifact."
        ),
    }
    return compiled
