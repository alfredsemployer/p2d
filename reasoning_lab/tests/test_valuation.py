import pytest

from p2d_reasoning_lab.valuation import ValenceAssessment, aggregate_valence


def _assessment(
    identifier: str, credence: float, group: str, reliability: float = 1.0
) -> ValenceAssessment:
    return ValenceAssessment(
        id=identifier,
        producer="test",
        credence=credence,
        reliability=reliability,
        independence_group=group,
    )


def test_valence_is_signed_and_forces_direction() -> None:
    positive = aggregate_valence([_assessment("a", 0.8, "one")])
    negative = aggregate_valence([_assessment("b", 0.2, "one")])
    assert positive["valence"] > 0
    assert positive["forced_binary_direction"] == "supported"
    assert negative["valence"] < 0
    assert negative["forced_binary_direction"] == "unsupported"


def test_exact_equipoise_is_zero() -> None:
    result = aggregate_valence([_assessment("a", 0.5, "one")])
    assert result["valence"] == pytest.approx(0.0)
    assert result["valence_sign"] == "zero"


def test_duplicate_dependent_vote_does_not_gain_independent_weight() -> None:
    single = aggregate_valence([_assessment("a", 0.8, "same")])
    duplicated = aggregate_valence(
        [
            _assessment("a", 0.8, "same"),
            _assessment("copy", 0.8, "same"),
        ]
    )
    assert duplicated["credence"] == pytest.approx(single["credence"])
    assert len(duplicated["clusters"]) == 1


def test_invalid_credence_is_rejected() -> None:
    with pytest.raises(ValueError):
        _assessment("bad", 1.1, "one")
