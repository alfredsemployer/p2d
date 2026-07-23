"""Executable verdict-policy semantics from specification version 0.2."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal


Strength = Literal["none", "weak", "moderate", "strong", "decisive"]
Direction = Literal["support", "opposition"]
EvidentialState = Literal["supported", "refuted", "contested", "insufficient"]
CoverageState = Literal["adequate", "limited", "not_assessed"]

STRENGTH_ORDER: dict[Strength, int] = {
    "none": 0,
    "weak": 1,
    "moderate": 2,
    "strong": 3,
    "decisive": 4,
}


@dataclass(frozen=True, slots=True)
class VerdictPolicy:
    id: str = "descriptive-v0.2"
    version: str = "0.2.0"
    ground_floor: Strength = "moderate"
    argument_floor: Strength = "moderate"
    require_adequate_coverage_for_terminal: bool = True
    unresolved_undercutter_blocks_route: bool = True
    normalization_required_for_cross_estimate: bool = True

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RouteAssessment:
    id: str
    direction: Direction
    ground_strength: Strength
    argument_strength: Strength
    unresolved_undercutter: bool = False
    normalization_required: bool = False
    normalization_satisfied: bool = True
    evidence_cluster_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class VerdictResult:
    evidential_state: EvidentialState
    coverage_state: CoverageState
    terminal_allowed: bool
    qualifying_support_routes: tuple[str, ...]
    qualifying_opposition_routes: tuple[str, ...]
    policy_id: str
    policy_version: str

    def to_dict(self) -> dict:
        return asdict(self)


def route_qualifies(route: RouteAssessment, policy: VerdictPolicy) -> bool:
    if STRENGTH_ORDER[route.ground_strength] < STRENGTH_ORDER[policy.ground_floor]:
        return False
    if (
        STRENGTH_ORDER[route.argument_strength]
        < STRENGTH_ORDER[policy.argument_floor]
    ):
        return False
    if policy.unresolved_undercutter_blocks_route and route.unresolved_undercutter:
        return False
    if (
        policy.normalization_required_for_cross_estimate
        and route.normalization_required
        and not route.normalization_satisfied
    ):
        return False
    return True


def derive_verdict(
    routes: list[RouteAssessment],
    *,
    coverage_state: CoverageState,
    policy: VerdictPolicy,
    coverage_exemption: bool = False,
) -> VerdictResult:
    support = tuple(
        route.id
        for route in routes
        if route.direction == "support" and route_qualifies(route, policy)
    )
    opposition = tuple(
        route.id
        for route in routes
        if route.direction == "opposition" and route_qualifies(route, policy)
    )
    if support and opposition:
        state: EvidentialState = "contested"
    elif support:
        state = "supported"
    elif opposition:
        state = "refuted"
    else:
        state = "insufficient"
    terminal_allowed = (
        coverage_exemption
        or not policy.require_adequate_coverage_for_terminal
        or coverage_state == "adequate"
    )
    return VerdictResult(
        evidential_state=state,
        coverage_state=coverage_state,
        terminal_allowed=terminal_allowed,
        qualifying_support_routes=support,
        qualifying_opposition_routes=opposition,
        policy_id=policy.id,
        policy_version=policy.version,
    )


def dependence_sensitivity(
    scenarios: dict[str, list[RouteAssessment]],
    *,
    coverage_state: CoverageState,
    policy: VerdictPolicy,
) -> dict:
    results = {
        name: derive_verdict(
            routes,
            coverage_state=coverage_state,
            policy=policy,
        )
        for name, routes in scenarios.items()
    }
    states = {result.evidential_state for result in results.values()}
    return {
        "stable": len(states) == 1,
        "stable_state": next(iter(states)) if len(states) == 1 else None,
        "scenarios": {name: result.to_dict() for name, result in results.items()},
    }
