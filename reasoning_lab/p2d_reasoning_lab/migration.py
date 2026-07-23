"""Explicit migration of legacy runs into the native v0.3 artifact contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .compiler import compile_reasoning_artifact


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def migrate_legacy_run(
    run_dir: str | Path,
    *,
    valence_decisions_path: str | Path,
) -> dict[str, Any]:
    """Compile a legacy reconstructed graph using explicit migration decisions.

    The migration refuses to infer signed valence from ``supported``,
    ``insufficient``, or coverage labels.
    """

    root = Path(run_dir)
    source = _load(root / "argument_graph_reconstructed.json")
    portfolio = _load(root / "question_portfolio.json")
    research = _load(root / "research_index.json")
    grounds = _load(root / "normalized_grounds.json")
    decisions = _load(Path(valence_decisions_path))
    by_claim = {str(item["claim_id"]): item for item in decisions}

    graph = {
        key: value
        for key, value in source.items()
        if key
        not in {
            "projection_contract",
            "structural_validation",
            "inferential_reachability",
            "generated_at",
            "schema_version",
        }
    }
    migrated_claims: list[dict[str, Any]] = []
    for source_claim in source.get("claims") or []:
        claim = dict(source_claim)
        display = dict(claim.pop("display_assessment", {}) or {})
        identifier = str(claim["id"])
        if identifier not in by_claim:
            raise ValueError(
                f"missing explicit signed-valence migration decision for {identifier}"
            )
        decision = by_claim[identifier]
        claim["source_research_claim_ids"] = list(
            display.get("source_claim_assessment_ids") or []
        )
        claim["independent_review_status"] = decision.get(
            "independent_review_status", "pending"
        )
        claim["valence_assessments"] = [
            {
                "id": f"VA-{identifier}-migration",
                "producer": decision.get(
                    "producer", "legacy-artifact-migration-fixture"
                ),
                "credence": decision["credence"],
                "reliability": decision.get("reliability", 0.5),
                "independence_group": f"legacy-migration:{identifier}",
                "calibration_state": "legacy_migration",
                "rationale": decision["rationale"],
                "method": "explicit_legacy_migration_decision",
            }
        ]
        migrated_claims.append(claim)
    graph["claims"] = migrated_claims
    graph["migration"] = {
        "source_artifact": "argument_graph_reconstructed.json",
        "valence_decisions": str(valence_decisions_path),
        "warning": (
            "Signed values are explicit, uncalibrated migration fixture decisions. "
            "They are not inferred from legacy evidence-state or coverage labels."
        ),
    }

    compiled = compile_reasoning_artifact(
        graph=graph,
        portfolio=portfolio,
        research=research,
        grounds=grounds,
        artifact_id=f"p2d:{root.name}:v0.3-migration",
    )
    _save(root / "reasoning_artifact_v03.json", compiled)
    _save(root / "visual_projection_v03.json", compiled["visual_projection"])
    return compiled
