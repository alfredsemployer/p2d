import pytest

from p2d_reasoning_lab.calibration import calibration_report


def test_calibration_is_separated_by_claim_type() -> None:
    report = calibration_report(
        [
            {"credence": 0.9, "outcome": 1, "claim_type": "empirical"},
            {"credence": 0.1, "outcome": 0, "claim_type": "empirical"},
            {"credence": 0.8, "outcome": 0, "claim_type": "interpretive"},
        ],
        bins=5,
    )
    assert set(report["by_claim_type"]) == {"empirical", "interpretive"}
    assert report["overall"]["calibration_state"] == "diagnostic_only"
    assert report["by_claim_type"]["empirical"]["brier_score"] == pytest.approx(
        0.01
    )


def test_invalid_outcome_is_rejected() -> None:
    with pytest.raises(ValueError):
        calibration_report(
            [{"credence": 0.8, "outcome": 2, "claim_type": "empirical"}]
        )
