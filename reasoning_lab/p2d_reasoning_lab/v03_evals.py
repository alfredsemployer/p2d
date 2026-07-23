"""Offline contract evaluations for compiled v0.3 reasoning artifacts."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .formal import cross_check_propositional


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _check(
    identifier: str,
    description: str,
    predicate: Callable[[], bool],
) -> dict[str, Any]:
    try:
        passed = bool(predicate())
        error = ""
    except Exception as exc:  # a contract check must fail visibly
        passed = False
        error = f"{type(exc).__name__}: {exc}"
    return {
        "id": identifier,
        "description": description,
        "passed": passed,
        "error": error,
    }


def evaluate_v03_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    claims = list(artifact.get("claims") or [])
    claim_ids = {str(item.get("id")) for item in claims}
    projection = dict(artifact.get("visual_projection") or {})
    cards = list(projection.get("cards") or [])
    card_ids = {str(item.get("claim_id")) for item in cards}
    arguments = list(artifact.get("arguments") or [])
    defeaters = list(artifact.get("defeaters") or [])

    checks = [
        _check(
            "V03-01",
            "structural validator reports no errors",
            lambda: not [
                item
                for item in artifact.get("structural_validation") or []
                if item.get("severity") == "error"
            ],
        ),
        _check(
            "V03-02",
            "each claim has one unique stable identity",
            lambda: len({item["claim_uid"] for item in claims}) == len(claims),
        ),
        _check(
            "V03-03",
            "projection cards are exactly the claim vertices",
            lambda: card_ids == claim_ids and len(cards) == len(claims),
        ),
        _check(
            "V03-04",
            "arguments and defeaters are never projected as cards",
            lambda: not (
                card_ids
                & {
                    str(item.get("id"))
                    for item in arguments + defeaters
                }
            ),
        ),
        _check(
            "V03-05",
            "every projected direction matches signed valence",
            lambda: all(
                item.get("direction_label")
                == ("supported" if float(item["valence"]) >= 0 else "unsupported")
                for item in cards
            ),
        ),
        _check(
            "V03-06",
            "valence is exactly 2p-1 and preserves assessment provenance",
            lambda: all(
                abs(
                    float(item["epistemic_assessment"]["valence"])
                    - (
                        2.0
                        * float(item["epistemic_assessment"]["credence"])
                        - 1.0
                    )
                )
                < 1e-9
                and bool(item["epistemic_assessment"]["assessments"])
                for item in claims
            ),
        ),
        _check(
            "V03-07",
            "coverage and evidence depth are separate complete records",
            lambda: all(
                "coverage_state" in item.get("coverage_record", {})
                and "segments_filled" in item.get("evidence_depth", {})
                and "credence" not in item.get("coverage_record", {})
                for item in claims
            ),
        ),
        _check(
            "V03-08",
            "every claim has explicit source-dependence scenarios",
            lambda: all(
                bool(
                    item.get("source_dependence", {}).get(
                        "sensitivity_scenarios"
                    )
                )
                for item in claims
            ),
        ),
        _check(
            "V03-09",
            "every visible relation has a claim origin",
            lambda: all(
                set(item.get("premise_claim_ids") or []).issubset(claim_ids)
                and bool(item.get("premise_claim_ids"))
                for item in projection.get("arguments") or []
            )
            and all(
                set(item.get("premise_claim_ids") or []).issubset(claim_ids)
                and bool(item.get("premise_claim_ids"))
                for item in projection.get("defeaters") or []
            ),
        ),
        _check(
            "V03-10",
            "formal report distinguishes checked from unsuitable arguments",
            lambda: (
                artifact["formal_validation"]["formal_candidates_checked"]
                + artifact["formal_validation"][
                    "unsuitable_for_strict_formalization"
                ]
                == len(arguments)
            ),
        ),
        _check(
            "V03-11",
            "defeasible engine produced one status for every argument",
            lambda: len(artifact["defeasible_evaluation"]["arguments"])
            == len(arguments),
        ),
        _check(
            "V03-12",
            "all active questions have terminal claims",
            lambda: all(
                bool(ids)
                for ids in artifact.get(
                    "terminal_claim_ids_by_question", {}
                ).values()
            ),
        ),
    ]

    formal_regressions = [
        (
            "modus_ponens",
            ["implies(P, Q)", "P"],
            "Q",
            "proved",
        ),
        (
            "affirming_the_consequent",
            ["implies(P, Q)", "Q"],
            "P",
            "disproved",
        ),
        (
            "inconsistent_premises",
            ["P", "not P"],
            "Q",
            "inconsistent_premises",
        ),
    ]
    formal_results = []
    for name, premises, conclusion, expected in formal_regressions:
        result = cross_check_propositional(
            premises,
            conclusion,
            formalization_fidelity="exact_for_stated_scope",
        )
        observed = result["z3"]["status"]
        formal_results.append(
            {
                "id": name,
                "expected": expected,
                "observed": observed,
                "passed": observed == expected and result["agreement"],
            }
        )

    passed = sum(item["passed"] for item in checks)
    formal_passed = sum(item["passed"] for item in formal_results)
    return {
        "suite": "p2d-v0.3-offline-contract",
        "generated_at": datetime.now(UTC).isoformat(),
        "artifact_id": artifact.get("artifact_id"),
        "contract_checks": {
            "passed": passed,
            "total": len(checks),
            "results": checks,
        },
        "formal_solver_regressions": {
            "passed": formal_passed,
            "total": len(formal_results),
            "results": formal_results,
        },
        "overall_pass": passed == len(checks)
        and formal_passed == len(formal_results),
        "limits": [
            "These checks validate contracts and deterministic behavior, not world truth.",
            "Legacy migration valences remain uncalibrated pending external labels.",
            "The Kimi graph contains no suitable strict empirical inference, so its solver coverage is correctly zero.",
        ],
    }


def run_v03_evaluations(
    *,
    artifact_path: str | Path,
    output_dir: str | Path,
) -> dict[str, Any]:
    artifact = _load(Path(artifact_path))
    result = evaluate_v03_artifact(artifact)
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    (target / "eval_results.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# p2d v0.3 offline evaluation",
        "",
        f"- Artifact: `{result['artifact_id']}`",
        f"- Contract checks: {result['contract_checks']['passed']}/{result['contract_checks']['total']}",
        f"- Formal solver regressions: {result['formal_solver_regressions']['passed']}/{result['formal_solver_regressions']['total']}",
        f"- Overall pass: `{str(result['overall_pass']).lower()}`",
        "",
        "## Limits",
        "",
        *[f"- {item}" for item in result["limits"]],
        "",
    ]
    (target / "eval_report.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    return result
