from p2d_reasoning_lab.defeasible import evaluate_defeasible_graph
from p2d_reasoning_lab.projection import build_visual_projection


def _graph() -> dict:
    return {
        "claims": [
            {
                "id": "C1",
                "proposition": "Premise",
                "epistemic_assessment": {
                    "valence": 0.4,
                    "valence_sign": "positive",
                    "forced_binary_direction": "supported",
                },
                "coverage_record": {"coverage_state": "limited", "harvey_quarters": 1},
                "evidence_depth": {"segments_filled": 2, "segments_total": 5},
            },
            {
                "id": "C2",
                "proposition": "Answer",
                "epistemic_assessment": {
                    "valence": -0.2,
                    "valence_sign": "negative",
                    "forced_binary_direction": "unsupported",
                },
                "coverage_record": {"coverage_state": "moderate", "harvey_quarters": 2},
                "evidence_depth": {"segments_filled": 3, "segments_total": 5},
            },
        ],
        "arguments": [
            {
                "id": "A1",
                "premise_claim_ids": ["C1"],
                "conclusion_claim_id": "C2",
                "assessment": "strong",
            }
        ],
        "defeaters": [],
        "terminal_claim_ids_by_question": {"Q1": ["C2"]},
    }


def test_arguments_are_edges_and_only_claims_become_cards() -> None:
    projection = build_visual_projection(_graph())
    assert {item["claim_id"] for item in projection["cards"]} == {"C1", "C2"}
    assert projection["arguments"][0]["argument_id"] == "A1"
    answer = next(item for item in projection["cards"] if item["claim_id"] == "C2")
    assert answer["designation"] == "answer"
    assert answer["direction_label"] == "unsupported"


def test_supported_claim_backed_defeater_rejects_argument() -> None:
    graph = _graph()
    graph["defeaters"] = [
        {
            "id": "D1",
            "target_id": "A1",
            "premise_claim_ids": ["C1"],
            "status": "supported",
        }
    ]
    result = evaluate_defeasible_graph(graph)
    assert result["arguments"][0]["dialectical_status"] == "rejected"
