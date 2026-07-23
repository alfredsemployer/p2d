from p2d_reasoning_lab.identity import (
    attach_claim_identity,
    exact_correspondence,
)


def test_superficial_whitespace_does_not_change_claim_identity() -> None:
    left = {"proposition": "K3 is competitive.", "temporal_scope": "2026"}
    right = {"proposition": "  K3   is competitive. ", "temporal_scope": "2026"}
    assert exact_correspondence(left, right)
    assert attach_claim_identity(left)["claim_uid"] == attach_claim_identity(right)[
        "claim_uid"
    ]


def test_scope_change_prevents_automatic_merge() -> None:
    left = {"proposition": "K3 is competitive.", "temporal_scope": "2026"}
    right = {"proposition": "K3 is competitive.", "temporal_scope": "2027"}
    assert not exact_correspondence(left, right)
