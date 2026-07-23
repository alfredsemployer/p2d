"""Evaluation harness for claim identity, answer entailment, policy, and logic."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .budget import BudgetExceeded, BudgetLedger
from .formal import cross_check_propositional
from .openrouter import OpenRouterClient
from .validation import validate_graph_skeleton
from .verdict import RouteAssessment, VerdictPolicy, derive_verdict


EVAL_MODEL = "openai/gpt-5.6-luna"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def evaluate_formal_cases(path: Path) -> dict[str, Any]:
    rows = []
    for case in _load(path):
        result = cross_check_propositional(
            case["premises"],
            case["conclusion"],
            formalization_fidelity=case["fidelity"],
        )
        observed = result["z3"]["status"]
        rows.append(
            {
                "id": case["id"],
                "expected": case["expected"],
                "observed": observed,
                "correct": observed == case["expected"],
                "backend_agreement": result["agreement"],
                "result": result,
            }
        )
    return {
        "name": "formal_entailment",
        "cases": len(rows),
        "accuracy": sum(item["correct"] for item in rows) / len(rows),
        "cross_backend_agreement": sum(
            item["backend_agreement"] for item in rows
        )
        / len(rows),
        "failures": [item for item in rows if not item["correct"]],
        "results": rows,
    }


def evaluate_verdict_policy() -> dict[str, Any]:
    policy = VerdictPolicy()
    cases = [
        {
            "id": "VP01",
            "routes": [
                RouteAssessment("s", "support", "strong", "moderate")
            ],
            "coverage": "adequate",
            "expected": ("supported", True),
        },
        {
            "id": "VP02",
            "routes": [
                RouteAssessment("s", "support", "strong", "moderate")
            ],
            "coverage": "limited",
            "expected": ("supported", False),
        },
        {
            "id": "VP03",
            "routes": [
                RouteAssessment("s", "support", "strong", "strong"),
                RouteAssessment("o", "opposition", "strong", "moderate"),
            ],
            "coverage": "adequate",
            "expected": ("contested", True),
        },
        {
            "id": "VP04",
            "routes": [RouteAssessment("s", "support", "weak", "strong")],
            "coverage": "adequate",
            "expected": ("insufficient", True),
        },
        {
            "id": "VP05",
            "routes": [
                RouteAssessment(
                    "s",
                    "support",
                    "strong",
                    "strong",
                    unresolved_undercutter=True,
                )
            ],
            "coverage": "adequate",
            "expected": ("insufficient", True),
        },
        {
            "id": "VP06",
            "routes": [
                RouteAssessment(
                    "s",
                    "support",
                    "strong",
                    "strong",
                    normalization_required=True,
                    normalization_satisfied=False,
                )
            ],
            "coverage": "adequate",
            "expected": ("insufficient", True),
        },
    ]
    rows = []
    for case in cases:
        result = derive_verdict(
            case["routes"],
            coverage_state=case["coverage"],
            policy=policy,
        )
        observed = (result.evidential_state, result.terminal_allowed)
        rows.append(
            {
                "id": case["id"],
                "expected": case["expected"],
                "observed": observed,
                "correct": observed == case["expected"],
                "result": result.to_dict(),
            }
        )
    return {
        "name": "verdict_policy",
        "cases": len(rows),
        "accuracy": sum(item["correct"] for item in rows) / len(rows),
        "failures": [item for item in rows if not item["correct"]],
        "results": rows,
    }


def evaluate_graph_structure(run_dir: Path) -> dict[str, Any]:
    portfolio = _load(run_dir / "question_portfolio.json")
    active_ids = {
        item["id"]
        for item in portfolio["questions"]
        if item.get("disposition") == "active"
    }
    grounds = _load(run_dir / "normalized_grounds.json")
    known_ground_ids = {item["id"] for item in grounds}
    cases = [
        (
            "GS01",
            "argument_graph_skeleton.json",
            False,
        ),
        (
            "GS02",
            "argument_graph_completed.json",
            True,
        ),
    ]
    rows = []
    for case_id, artifact, expected_valid in cases:
        issues = validate_graph_skeleton(
            _load(run_dir / artifact),
            active_question_ids=active_ids,
            known_ground_ids=known_ground_ids,
        )
        errors = [item.to_dict() for item in issues if item.severity == "error"]
        observed_valid = not errors
        rows.append(
            {
                "id": case_id,
                "artifact": artifact,
                "expected_valid": expected_valid,
                "observed_valid": observed_valid,
                "correct": observed_valid == expected_valid,
                "errors": errors,
            }
        )
    return {
        "name": "graph_structure",
        "cases": len(rows),
        "accuracy": sum(item["correct"] for item in rows) / len(rows),
        "false_pass_rate": sum(
            item["observed_valid"] and not item["expected_valid"] for item in rows
        )
        / len(rows),
        "failures": [item for item in rows if not item["correct"]],
        "results": rows,
    }


def evaluate_claim_correspondence(
    client: OpenRouterClient, path: Path, *, model: str = EVAL_MODEL
) -> dict[str, Any]:
    cases = _load(path)
    prompt = f"""Classify each ordered claim pair. Return one result per ID.
Labels:
- equivalent: same proposition under the stated scope;
- entails: A entails B but B does not entail A;
- entailed_by: B entails A but A does not entail B;
- overlapping_scope: propositions overlap but neither safely entails the other;
- same_topic_distinct_proposition: related subject, materially different claim;
- unrelated: no material propositional relationship.

False equivalence is much worse than a conservative non-merge. Do not import
unstated background premises. Return JSON:
{{"results":[{{"id":"CC01","label":"","confidence":0.0,"reason":""}}]}}

CASES:
{json.dumps(cases, ensure_ascii=False)}"""
    prediction, reply = client.call_json(
        purpose="eval:claim_correspondence",
        model=model,
        prompt=prompt,
        max_tokens=3000,
        temperature=0,
    )
    predicted = {item["id"]: item for item in prediction.get("results", [])}
    rows = []
    for case in cases:
        item = predicted.get(case["id"], {})
        observed = item.get("label", "missing")
        correct = observed == case["expected"]
        false_merge = observed == "equivalent" and case["expected"] != "equivalent"
        missed_merge = case["expected"] == "equivalent" and observed != "equivalent"
        rows.append(
            {
                **case,
                "observed": observed,
                "correct": correct,
                "false_merge": false_merge,
                "missed_merge": missed_merge,
                "model_reason": item.get("reason", ""),
                "confidence": item.get("confidence"),
            }
        )
    false_merges = sum(item["false_merge"] for item in rows)
    other_errors = sum(
        not item["correct"] and not item["false_merge"] for item in rows
    )
    return {
        "name": "claim_correspondence",
        "model": reply.model,
        "response_id": reply.response_id,
        "cases": len(rows),
        "accuracy": sum(item["correct"] for item in rows) / len(rows),
        "false_merge_rate": false_merges / len(rows),
        "missed_merge_rate": sum(item["missed_merge"] for item in rows)
        / len(rows),
        "weighted_error": (5 * false_merges + other_errors) / len(rows),
        "failures": [item for item in rows if not item["correct"]],
        "results": rows,
    }


def evaluate_answer_entailment(
    client: OpenRouterClient, path: Path, *, model: str = EVAL_MODEL
) -> dict[str, Any]:
    cases = _load(path)
    prompt = f"""Audit whether each answer sentence stays within its supporting
claims. Labels:
- entailed
- unsupported_strengthening
- unsupported_synthesis
- scope_drift
- modality_drift
- precision_drift
- failure_to_false

Treat factual context as material. "No evidence found in a bounded search" does
not entail universal absence. A failed argument does not refute its conclusion.
Return JSON:
{{"results":[{{"id":"AE01","label":"","reason":""}}]}}

CASES:
{json.dumps(cases, ensure_ascii=False)}"""
    prediction, reply = client.call_json(
        purpose="eval:answer_entailment",
        model=model,
        prompt=prompt,
        max_tokens=2200,
        temperature=0,
    )
    predicted = {item["id"]: item for item in prediction.get("results", [])}
    rows = []
    for case in cases:
        item = predicted.get(case["id"], {})
        observed = item.get("label", "missing")
        rows.append(
            {
                **case,
                "observed": observed,
                "correct": observed == case["expected"],
                "model_reason": item.get("reason", ""),
            }
        )
    return {
        "name": "answer_entailment",
        "model": reply.model,
        "response_id": reply.response_id,
        "cases": len(rows),
        "accuracy": sum(item["correct"] for item in rows) / len(rows),
        "false_pass_rate": sum(
            item["observed"] == "entailed" and item["expected"] != "entailed"
            for item in rows
        )
        / len(rows),
        "failures": [item for item in rows if not item["correct"]],
        "results": rows,
    }


def run_evaluations(
    *,
    eval_dir: str | Path,
    output_dir: str | Path,
    ledger_path: str | Path,
    api_key: str,
    budget_usd: float,
    eval_model: str = EVAL_MODEL,
) -> dict[str, Any]:
    source = Path(eval_dir)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    ledger = BudgetLedger(ledger_path, limit_usd=budget_usd)
    client = OpenRouterClient(api_key, ledger)

    results: dict[str, Any] = {
        "formal_entailment": evaluate_formal_cases(
            source / "formal_entailment.json"
        ),
        "verdict_policy": evaluate_verdict_policy(),
        "graph_structure": evaluate_graph_structure(output.parent),
    }
    for name, function, file_name in (
        (
            "claim_correspondence",
            evaluate_claim_correspondence,
            "claim_correspondence.json",
        ),
        ("answer_entailment", evaluate_answer_entailment, "answer_entailment.json"),
    ):
        try:
            results[name] = function(
                client, source / file_name, model=eval_model
            )
        except (BudgetExceeded, RuntimeError, ValueError) as exc:
            results[name] = {"name": name, "error": str(exc)}

    completed = [
        item for item in results.values() if isinstance(item, dict) and "accuracy" in item
    ]
    summary = {
        "run_at": datetime.now(UTC).isoformat(),
        "suites": len(results),
        "completed_suites": len(completed),
        "mean_accuracy": (
            sum(float(item["accuracy"]) for item in completed) / len(completed)
            if completed
            else None
        ),
        "budget": ledger.summary(),
        "results": results,
    }
    _save(output / "eval_results.json", summary)

    lines = [
        "# Evaluation report",
        "",
        f"Run: {summary['run_at']}",
        f"OpenRouter spend after evaluations: ${ledger.spent}",
        "",
        "| Suite | Cases | Accuracy | Critical metric |",
        "|---|---:|---:|---|",
    ]
    for name, item in results.items():
        if "error" in item:
            lines.append(f"| {name} | — | — | ERROR: {item['error']} |")
            continue
        critical = ""
        if name == "claim_correspondence":
            critical = f"false merge {item['false_merge_rate']:.1%}"
        elif name == "answer_entailment":
            critical = f"false pass {item['false_pass_rate']:.1%}"
        elif name == "graph_structure":
            critical = f"false pass {item['false_pass_rate']:.1%}"
        elif name == "formal_entailment":
            critical = f"backend agreement {item['cross_backend_agreement']:.1%}"
        lines.append(
            f"| {name} | {item['cases']} | {item['accuracy']:.1%} | {critical} |"
        )
    lines.extend(["", "Failures remain in `eval_results.json` with case-level reasons."])
    (output / "eval_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary
