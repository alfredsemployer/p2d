"""Calibration reports for resolved claim assessments."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any


def _metrics(cases: list[dict[str, Any]], *, bins: int) -> dict[str, Any]:
    if not cases:
        return {"cases": 0, "calibration_state": "no_resolved_cases"}
    probabilities = [float(item["credence"]) for item in cases]
    outcomes = [int(item["outcome"]) for item in cases]
    for probability in probabilities:
        if not 0.0 <= probability <= 1.0:
            raise ValueError("credence must be in [0,1]")
    if any(outcome not in {0, 1} for outcome in outcomes):
        raise ValueError("outcome must be 0 or 1")

    brier = sum(
        (probability - outcome) ** 2
        for probability, outcome in zip(probabilities, outcomes, strict=True)
    ) / len(cases)
    log_loss = -sum(
        outcome * math.log(min(max(probability, 1e-12), 1 - 1e-12))
        + (1 - outcome)
        * math.log(min(max(1 - probability, 1e-12), 1 - 1e-12))
        for probability, outcome in zip(probabilities, outcomes, strict=True)
    ) / len(cases)
    accuracy = sum(
        (probability >= 0.5) == bool(outcome)
        for probability, outcome in zip(probabilities, outcomes, strict=True)
    ) / len(cases)
    decisiveness = sum(abs(probability - 0.5) * 2 for probability in probabilities) / len(cases)

    bucketed: dict[int, list[tuple[float, int]]] = defaultdict(list)
    for probability, outcome in zip(probabilities, outcomes, strict=True):
        index = min(bins - 1, int(probability * bins))
        bucketed[index].append((probability, outcome))
    ece = 0.0
    bucket_records = []
    for index in range(bins):
        values = bucketed.get(index, [])
        if not values:
            continue
        mean_prediction = sum(item[0] for item in values) / len(values)
        empirical_rate = sum(item[1] for item in values) / len(values)
        weight = len(values) / len(cases)
        ece += weight * abs(mean_prediction - empirical_rate)
        bucket_records.append(
            {
                "lower": index / bins,
                "upper": (index + 1) / bins,
                "cases": len(values),
                "mean_prediction": mean_prediction,
                "empirical_rate": empirical_rate,
            }
        )
    return {
        "cases": len(cases),
        "brier_score": brier,
        "log_loss": log_loss,
        "binary_accuracy": accuracy,
        "mean_decisiveness": decisiveness,
        "expected_calibration_error": ece,
        "bins": bucket_records,
        "calibration_state": (
            "diagnostic_only" if len(cases) < 100 else "eligible_for_review"
        ),
    }


def calibration_report(
    cases: list[dict[str, Any]], *, bins: int = 10
) -> dict[str, Any]:
    """Report calibration globally and by claim type.

    The function deliberately never self-certifies a model as calibrated.
    Release eligibility remains a reviewed policy decision.
    """

    if bins < 2:
        raise ValueError("bins must be at least 2")
    by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case in cases:
        by_type[str(case.get("claim_type") or "unknown")].append(case)
    return {
        "policy": "resolved-claim-calibration-v1",
        "overall": _metrics(cases, bins=bins),
        "by_claim_type": {
            name: _metrics(items, bins=bins)
            for name, items in sorted(by_type.items())
        },
        "release_note": (
            "Metrics diagnose calibration; they do not by themselves authorize "
            "probability language for a different claim type or horizon."
        ),
    }
