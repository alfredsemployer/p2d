"""Signed claim valence with provenance-preserving deterministic aggregation."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Literal


ValenceSign = Literal["positive", "negative", "zero"]
CalibrationState = Literal["calibrated", "uncalibrated", "legacy_migration"]


@dataclass(frozen=True, slots=True)
class ValenceAssessment:
    id: str
    producer: str
    credence: float
    reliability: float = 1.0
    independence_group: str = ""
    calibration_state: CalibrationState = "uncalibrated"
    rationale: str = ""
    method: str = "explicit_assessment"

    def __post_init__(self) -> None:
        if not 0.0 <= self.credence <= 1.0:
            raise ValueError("credence must be in [0, 1]")
        if not 0.0 <= self.reliability <= 1.0:
            raise ValueError("reliability must be in [0, 1]")
        if not self.id:
            raise ValueError("assessment id is required")
        if not self.producer:
            raise ValueError("assessment producer is required")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _sign(valence: float, *, tolerance: float = 1e-12) -> ValenceSign:
    if abs(valence) <= tolerance:
        return "zero"
    return "positive" if valence > 0 else "negative"


def _bounded_probability(value: float) -> float:
    return min(max(value, 1e-9), 1.0 - 1e-9)


def _logit(probability: float) -> float:
    p = _bounded_probability(probability)
    return math.log(p / (1.0 - p))


def _sigmoid(value: float) -> float:
    if value >= 0:
        scale = math.exp(-value)
        return 1.0 / (1.0 + scale)
    scale = math.exp(value)
    return scale / (1.0 + scale)


def aggregate_valence(
    assessments: list[ValenceAssessment],
    *,
    prior_credence: float = 0.5,
) -> dict[str, Any]:
    """Aggregate assessments without double-counting dependent model passes.

    Assessments in the same independence group are first averaged into one
    cluster opinion. Cluster opinions are then combined as reliability-weighted
    log-odds updates relative to the stated prior.
    """

    if not assessments:
        raise ValueError("at least one explicit valence assessment is required")
    if not 0.0 < prior_credence < 1.0:
        raise ValueError("prior_credence must be strictly between 0 and 1")

    grouped: dict[str, list[ValenceAssessment]] = {}
    for item in assessments:
        key = item.independence_group or f"assessment:{item.id}"
        grouped.setdefault(key, []).append(item)

    prior_logit = _logit(prior_credence)
    cluster_records: list[dict[str, Any]] = []
    updates: list[float] = []
    weights: list[float] = []
    for group, members in sorted(grouped.items()):
        total_weight = sum(member.reliability for member in members)
        if total_weight == 0:
            cluster_credence = prior_credence
            cluster_reliability = 0.0
        else:
            cluster_credence = (
                sum(member.credence * member.reliability for member in members)
                / total_weight
            )
            # Repetition inside a dependence cluster cannot create more than
            # one independent unit of reliability.
            cluster_reliability = max(member.reliability for member in members)
        updates.append(
            (_logit(cluster_credence) - prior_logit) * cluster_reliability
        )
        weights.append(cluster_reliability)
        cluster_records.append(
            {
                "independence_group": group,
                "assessment_ids": [member.id for member in members],
                "credence": cluster_credence,
                "reliability": cluster_reliability,
            }
        )

    if sum(weights) == 0:
        aggregate_credence = prior_credence
    else:
        aggregate_credence = _sigmoid(
            prior_logit + sum(updates) / sum(weights)
        )
    valence = 2.0 * aggregate_credence - 1.0
    calibration_states = {item.calibration_state for item in assessments}
    calibration_state: CalibrationState
    if calibration_states == {"calibrated"}:
        calibration_state = "calibrated"
    elif "legacy_migration" in calibration_states:
        calibration_state = "legacy_migration"
    else:
        calibration_state = "uncalibrated"

    return {
        "credence": aggregate_credence,
        "valence": valence,
        "valence_sign": _sign(valence),
        "forced_binary_direction": "supported" if valence >= 0 else "unsupported",
        "zero_policy": "zero only at exact epistemic equipoise",
        "prior_credence": prior_credence,
        "aggregation_policy": "dependence-clustered-log-odds-v1",
        "calibration_state": calibration_state,
        "clusters": cluster_records,
        "assessments": [item.to_dict() for item in assessments],
    }


def assessment_from_record(record: dict[str, Any]) -> ValenceAssessment:
    return ValenceAssessment(
        id=str(record["id"]),
        producer=str(record["producer"]),
        credence=float(record["credence"]),
        reliability=float(record.get("reliability", 1.0)),
        independence_group=str(record.get("independence_group") or ""),
        calibration_state=record.get("calibration_state", "uncalibrated"),
        rationale=str(record.get("rationale") or ""),
        method=str(record.get("method") or "explicit_assessment"),
    )
