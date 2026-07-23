"""Deterministic structural validation for v0.2 graph skeletons."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    severity: str
    code: str
    message: str
    target_id: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "target_id": self.target_id,
        }


def validate_graph_skeleton(
    graph: dict,
    *,
    active_question_ids: set[str] | None = None,
    known_ground_ids: set[str] | None = None,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    claims = list(graph.get("claims") or [])
    arguments = list(graph.get("arguments") or [])
    claim_ids = [str(item.get("id") or "") for item in claims]
    if not claims:
        issues.append(
            ValidationIssue("error", "no_claims", "Graph contains no claims.")
        )
    if len(claim_ids) != len(set(claim_ids)):
        issues.append(
            ValidationIssue(
                "error", "duplicate_claim_ids", "Claim IDs must be unique."
            )
        )
    known = set(claim_ids)
    if str(graph.get("schema_version") or "").startswith("0.3"):
        claim_uids = [str(item.get("claim_uid") or "") for item in claims]
        if not all(claim_uids) or len(claim_uids) != len(set(claim_uids)):
            issues.append(
                ValidationIssue(
                    "error",
                    "invalid_claim_identity",
                    "Every v0.3 claim must have a unique stable claim_uid.",
                )
            )
        for claim in claims:
            claim_id = str(claim.get("id") or "")
            assessment = dict(claim.get("epistemic_assessment") or {})
            try:
                credence = float(assessment["credence"])
                valence = float(assessment["valence"])
            except (KeyError, TypeError, ValueError):
                issues.append(
                    ValidationIssue(
                        "error",
                        "missing_signed_valence",
                        "Every v0.3 claim requires explicit credence and valence.",
                        claim_id,
                    )
                )
                continue
            expected_valence = 2.0 * credence - 1.0
            expected_sign = (
                "zero"
                if abs(expected_valence) <= 1e-12
                else "positive"
                if expected_valence > 0
                else "negative"
            )
            expected_direction = (
                "supported" if expected_valence >= 0 else "unsupported"
            )
            if not 0.0 <= credence <= 1.0 or abs(valence - expected_valence) > 1e-9:
                issues.append(
                    ValidationIssue(
                        "error",
                        "invalid_signed_valence",
                        "Valence must equal 2 × credence − 1.",
                        claim_id,
                    )
                )
            if assessment.get("valence_sign") != expected_sign:
                issues.append(
                    ValidationIssue(
                        "error",
                        "invalid_valence_sign",
                        "Valence sign does not match the signed value.",
                        claim_id,
                    )
                )
            if assessment.get("forced_binary_direction") != expected_direction:
                issues.append(
                    ValidationIssue(
                        "error",
                        "invalid_binary_direction",
                        "Displayed binary direction does not match signed valence.",
                        claim_id,
                    )
                )
            coverage = dict(claim.get("coverage_record") or {})
            if "coverage_state" not in coverage or "harvey_quarters" not in coverage:
                issues.append(
                    ValidationIssue(
                        "error",
                        "missing_coverage_record",
                        "Every v0.3 claim requires a separate coverage record.",
                        claim_id,
                    )
                )
    if not arguments:
        issues.append(
            ValidationIssue(
                "error",
                "no_arguments",
                "Graph contains claims but no inferential hyperedges.",
            )
        )
    argument_ids = [str(item.get("id") or "") for item in arguments]
    known_arguments = set(argument_ids)
    if len(argument_ids) != len(set(argument_ids)):
        issues.append(
            ValidationIssue(
                "error", "duplicate_argument_ids", "Argument IDs must be unique."
            )
        )
    for argument in arguments:
        target = str(argument.get("id") or "")
        conclusion = argument.get("conclusion_claim_id")
        if conclusion not in known:
            issues.append(
                ValidationIssue(
                    "error",
                    "unknown_conclusion",
                    f"Unknown conclusion claim {conclusion!r}.",
                    target,
                )
            )
        premises = list(argument.get("premise_claim_ids") or [])
        for premise in premises:
            if premise not in known:
                issues.append(
                    ValidationIssue(
                        "error",
                        "unknown_premise",
                        f"Unknown premise claim {premise!r}.",
                        target,
                    )
                )
        if conclusion in premises:
            issues.append(
                ValidationIssue(
                    "error",
                    "direct_circularity",
                    "Conclusion also appears as a premise.",
                    target,
                )
            )
        ground_ids = list(argument.get("ground_ids") or [])
        if known_ground_ids is not None:
            for ground_id in ground_ids:
                if ground_id not in known_ground_ids:
                    issues.append(
                        ValidationIssue(
                            "error",
                            "unknown_ground",
                            f"Unknown ground {ground_id!r}.",
                            target,
                        )
                    )
        if (
            not premises
            and not ground_ids
            and not argument.get("anticipated_ground_kinds")
        ):
            issues.append(
                ValidationIssue(
                    "error",
                    "empty_argument",
                    "Argument has neither premise claims nor anticipated grounds.",
                    target,
                )
            )
        if not str(argument.get("warrant_reconstruction") or "").strip():
            issues.append(
                ValidationIssue(
                    "error",
                    "missing_warrant_reconstruction",
                    "Argument has no warrant reconstruction.",
                    target,
                )
            )
    attempted_claims = {
        str(item.get("conclusion_claim_id") or "") for item in arguments
    }
    for claim_id in known - attempted_claims:
        issues.append(
            ValidationIssue(
                "error",
                "claim_without_argument_attempt",
                "Claim has no supporting argument attempt.",
                claim_id,
            )
        )

    defeaters = list(graph.get("defeaters") or [])
    defeater_ids = [str(item.get("id") or "") for item in defeaters]
    if len(defeater_ids) != len(set(defeater_ids)):
        issues.append(
            ValidationIssue(
                "error", "duplicate_defeater_ids", "Defeater IDs must be unique."
            )
        )
    for defeater in defeaters:
        target = str(defeater.get("id") or "")
        target_argument = str(defeater.get("target_id") or "")
        if target_argument not in known_arguments:
            issues.append(
                ValidationIssue(
                    "error",
                    "unknown_defeater_target",
                    f"Unknown target argument {target_argument!r}.",
                    target,
                )
            )
        premises = list(defeater.get("premise_claim_ids") or [])
        if not premises:
            issues.append(
                ValidationIssue(
                    "error",
                    "defeater_without_premise_claim",
                    "Defeater has no claim premise to serve as its visible origin.",
                    target,
                )
            )
        for premise in premises:
            if premise not in known:
                issues.append(
                    ValidationIssue(
                        "error",
                        "unknown_defeater_premise",
                        f"Unknown defeater premise claim {premise!r}.",
                        target,
                    )
                )
        if known_ground_ids is not None:
            for ground_id in defeater.get("ground_ids") or []:
                if ground_id not in known_ground_ids:
                    issues.append(
                        ValidationIssue(
                            "error",
                            "unknown_defeater_ground",
                            f"Unknown defeater ground {ground_id!r}.",
                            target,
                        )
                    )

    adjacency: dict[str, set[str]] = {claim_id: set() for claim_id in known}
    for argument in arguments:
        conclusion = str(argument.get("conclusion_claim_id") or "")
        for premise in argument.get("premise_claim_ids") or []:
            if premise in known and conclusion in known:
                adjacency[premise].add(conclusion)
    visiting: set[str] = set()
    visited: set[str] = set()

    def has_cycle(claim_id: str) -> bool:
        if claim_id in visiting:
            return True
        if claim_id in visited:
            return False
        visiting.add(claim_id)
        cyclic = any(has_cycle(child) for child in adjacency[claim_id])
        visiting.remove(claim_id)
        visited.add(claim_id)
        return cyclic

    if any(has_cycle(claim_id) for claim_id in known if claim_id not in visited):
        issues.append(
            ValidationIssue(
                "error",
                "dependency_cycle",
                "Claim dependencies contain an inferential cycle.",
            )
        )
    terminal_map = graph.get("terminal_claim_ids_by_question") or {}
    for question_id, terminal_ids in terminal_map.items():
        for claim_id in terminal_ids:
            if claim_id not in known:
                issues.append(
                    ValidationIssue(
                        "error",
                        "unknown_terminal_claim",
                        f"Unknown terminal claim {claim_id!r}.",
                        str(question_id),
                    )
                )
    if active_question_ids:
        for question_id in active_question_ids:
            if not terminal_map.get(question_id):
                issues.append(
                    ValidationIssue(
                        "error",
                        "question_without_terminal",
                        "Active question has no terminal claim.",
                        question_id,
                    )
                )

    projection = graph.get("projection_contract")
    if projection:
        coverage_mapping = dict(
            projection.get("coverage_harvey_mapping") or {}
        )
        scale_quarters = coverage_mapping.pop("scale_quarters", None)
        for claim in claims:
            claim_id = str(claim.get("id") or "")
            display = dict(claim.get("display_assessment") or {})
            evidential_state = display.get("evidential_state")
            expected_acceptance = (
                "supported"
                if evidential_state == "supported"
                else "not_supported"
            )
            if display.get("acceptance_status") != expected_acceptance:
                issues.append(
                    ValidationIssue(
                        "error",
                        "invalid_projection_acceptance",
                        (
                            "Claim acceptance status does not match the "
                            "projection contract."
                        ),
                        claim_id,
                    )
                )
            coverage_state = display.get("coverage_state")
            if coverage_state not in coverage_mapping:
                issues.append(
                    ValidationIssue(
                        "error",
                        "unknown_projection_coverage",
                        f"Coverage state {coverage_state!r} has no display mapping.",
                        claim_id,
                    )
                )
                continue
            coverage_display = dict(display.get("coverage_display") or {})
            if (
                coverage_display.get("harvey_quarters")
                != coverage_mapping[coverage_state]
                or coverage_display.get("scale_quarters") != scale_quarters
            ):
                issues.append(
                    ValidationIssue(
                        "error",
                        "invalid_projection_coverage_display",
                        (
                            "Claim Harvey-ball coverage does not match the "
                            "projection contract."
                        ),
                        claim_id,
                    )
                )
    return issues


def inferential_reachability_report(
    graph: dict,
    *,
    active_question_ids: set[str] | None = None,
) -> dict:
    """Report whether claims participate in grounded routes to terminals.

    An unresolved terminal may deliberately lack a complete grounded route.
    That is reported separately from structural errors so absence of support is
    not confused with malformed topology.
    """

    claims = list(graph.get("claims") or [])
    arguments = list(graph.get("arguments") or [])
    defeaters = list(graph.get("defeaters") or [])
    claim_ids = {str(item.get("id") or "") for item in claims}
    arguments_by_id = {
        str(item.get("id") or ""): item for item in arguments
    }
    concluding: dict[str, list[dict]] = {claim_id: [] for claim_id in claim_ids}
    forward: dict[str, set[str]] = {claim_id: set() for claim_id in claim_ids}
    dependency_edges = 0
    for argument in arguments:
        conclusion = str(argument.get("conclusion_claim_id") or "")
        if conclusion in concluding:
            concluding[conclusion].append(argument)
        for premise in argument.get("premise_claim_ids") or []:
            if premise in claim_ids and conclusion in claim_ids:
                forward[premise].add(conclusion)
                dependency_edges += 1

    terminal_map = graph.get("terminal_claim_ids_by_question") or {}
    terminal_ids = {
        claim_id
        for question_id, ids in terminal_map.items()
        if active_question_ids is None or question_id in active_question_ids
        for claim_id in ids
    }

    defeater_use: dict[str, set[str]] = {claim_id: set() for claim_id in claim_ids}
    for defeater in defeaters:
        target_argument = arguments_by_id.get(str(defeater.get("target_id") or ""))
        if not target_argument:
            continue
        target_conclusion = str(
            target_argument.get("conclusion_claim_id") or ""
        )
        for premise in defeater.get("premise_claim_ids") or []:
            if premise in claim_ids and target_conclusion in claim_ids:
                defeater_use[premise].add(target_conclusion)

    def reaches_terminal(start: str) -> bool:
        queue = [start]
        seen: set[str] = set()
        while queue:
            current = queue.pop()
            if current in seen:
                continue
            seen.add(current)
            if current in terminal_ids and current != start:
                return True
            queue.extend(forward[current] | defeater_use[current])
        return start in terminal_ids

    grounded_cache: dict[str, bool] = {}
    grounding_stack: set[str] = set()

    def has_complete_ground_route(claim_id: str) -> bool:
        if claim_id in grounded_cache:
            return grounded_cache[claim_id]
        if claim_id in grounding_stack:
            return False
        grounding_stack.add(claim_id)
        result = False
        for argument in concluding.get(claim_id, []):
            premises = list(argument.get("premise_claim_ids") or [])
            has_input = bool(argument.get("ground_ids")) or bool(premises)
            if has_input and all(has_complete_ground_route(item) for item in premises):
                result = True
                break
        grounding_stack.remove(claim_id)
        grounded_cache[claim_id] = result
        return result

    depth_cache: dict[str, int] = {}

    def depth(claim_id: str, stack: set[str] | None = None) -> int:
        if claim_id in depth_cache:
            return depth_cache[claim_id]
        active = set(stack or ())
        if claim_id in active:
            return 0
        active.add(claim_id)
        values = []
        for argument in concluding.get(claim_id, []):
            premises = list(argument.get("premise_claim_ids") or [])
            if premises:
                values.append(1 + max(depth(item, active) for item in premises))
            elif argument.get("ground_ids"):
                values.append(1)
        result = max(values, default=0)
        depth_cache[claim_id] = result
        return result

    orphan_nonterminals = sorted(
        claim_id
        for claim_id in claim_ids - terminal_ids
        if not reaches_terminal(claim_id)
    )
    terminals_without_attempts = sorted(
        claim_id for claim_id in terminal_ids if not concluding.get(claim_id)
    )
    terminals_without_complete_ground_route = sorted(
        claim_id
        for claim_id in terminal_ids
        if not has_complete_ground_route(claim_id)
    )
    return {
        "claim_dependency_edges": dependency_edges,
        "defeater_backing_edges": sum(len(items) for items in defeater_use.values()),
        "terminal_claims": len(terminal_ids),
        "claims_reaching_a_terminal": sum(
            reaches_terminal(claim_id) for claim_id in claim_ids
        ),
        "orphan_nonterminal_claim_ids": orphan_nonterminals,
        "terminal_claim_ids_without_argument_attempt": terminals_without_attempts,
        "terminal_claim_ids_without_complete_ground_route": (
            terminals_without_complete_ground_route
        ),
        "maximum_claim_dependency_depth": max(
            (depth(claim_id) for claim_id in terminal_ids),
            default=0,
        ),
        "structurally_connected": (
            dependency_edges > 0
            and not orphan_nonterminals
            and not terminals_without_attempts
        ),
    }
