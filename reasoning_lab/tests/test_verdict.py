from p2d_reasoning_lab.verdict import (
    RouteAssessment,
    VerdictPolicy,
    dependence_sensitivity,
    derive_verdict,
    route_qualifies,
)


def test_support_requires_both_floors():
    policy = VerdictPolicy()
    weak_ground = RouteAssessment("r", "support", "weak", "strong")
    weak_argument = RouteAssessment("r2", "support", "strong", "weak")
    assert not route_qualifies(weak_ground, policy)
    assert not route_qualifies(weak_argument, policy)


def test_contested_requires_qualifying_routes_in_both_directions():
    result = derive_verdict(
        [
            RouteAssessment("s", "support", "strong", "strong"),
            RouteAssessment("o", "opposition", "moderate", "moderate"),
        ],
        coverage_state="adequate",
        policy=VerdictPolicy(),
    )
    assert result.evidential_state == "contested"


def test_coverage_does_not_change_evidential_state():
    result = derive_verdict(
        [RouteAssessment("s", "support", "strong", "strong")],
        coverage_state="limited",
        policy=VerdictPolicy(),
    )
    assert result.evidential_state == "supported"
    assert result.terminal_allowed is False


def test_undercutter_blocks_route():
    result = derive_verdict(
        [
            RouteAssessment(
                "s",
                "support",
                "strong",
                "strong",
                unresolved_undercutter=True,
            )
        ],
        coverage_state="adequate",
        policy=VerdictPolicy(),
    )
    assert result.evidential_state == "insufficient"


def test_missing_normalization_blocks_cross_estimate_route():
    result = derive_verdict(
        [
            RouteAssessment(
                "s",
                "support",
                "strong",
                "strong",
                normalization_required=True,
                normalization_satisfied=False,
            )
        ],
        coverage_state="adequate",
        policy=VerdictPolicy(),
    )
    assert result.evidential_state == "insufficient"


def test_dependence_sensitivity_preserves_conditional_result():
    result = dependence_sensitivity(
        {
            "optimistic": [
                RouteAssessment("s", "support", "strong", "strong")
            ],
            "pessimistic": [
                RouteAssessment("s", "support", "weak", "strong")
            ],
        },
        coverage_state="adequate",
        policy=VerdictPolicy(),
    )
    assert result["stable"] is False
    assert (
        result["scenarios"]["optimistic"]["evidential_state"] == "supported"
    )
    assert (
        result["scenarios"]["pessimistic"]["evidential_state"] == "insufficient"
    )
