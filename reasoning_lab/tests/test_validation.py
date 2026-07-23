from p2d_reasoning_lab.validation import (
    inferential_reachability_report,
    validate_graph_skeleton,
)


def _claim(identifier):
    return {"id": identifier, "proposition": identifier}


def test_claims_without_arguments_fail():
    issues = validate_graph_skeleton(
        {
            "claims": [_claim("C1")],
            "arguments": [],
            "terminal_claim_ids_by_question": {"Q1": ["C1"]},
        },
        active_question_ids={"Q1"},
    )
    assert "no_arguments" in {item.code for item in issues}


def test_valid_ground_to_claim_argument_passes():
    issues = validate_graph_skeleton(
        {
            "claims": [_claim("C1")],
            "arguments": [
                {
                    "id": "A1",
                    "premise_claim_ids": [],
                    "anticipated_ground_kinds": ["measurement"],
                    "conclusion_claim_id": "C1",
                    "warrant_reconstruction": "Valid measurements bear on C1.",
                }
            ],
            "terminal_claim_ids_by_question": {"Q1": ["C1"]},
        },
        active_question_ids={"Q1"},
    )
    assert issues == []


def test_unresolved_references_fail():
    issues = validate_graph_skeleton(
        {
            "claims": [_claim("C1")],
            "arguments": [
                {
                    "id": "A1",
                    "premise_claim_ids": ["C2"],
                    "anticipated_ground_kinds": [],
                    "conclusion_claim_id": "C3",
                    "warrant_reconstruction": "x",
                }
            ],
            "terminal_claim_ids_by_question": {},
        },
        active_question_ids={"Q1"},
    )
    codes = {item.code for item in issues}
    assert {"unknown_premise", "unknown_conclusion", "question_without_terminal"} <= codes


def test_each_claim_requires_argument_attempt():
    issues = validate_graph_skeleton(
        {
            "claims": [_claim("C1"), _claim("C2")],
            "arguments": [
                {
                    "id": "A1",
                    "premise_claim_ids": [],
                    "anticipated_ground_kinds": ["measurement"],
                    "conclusion_claim_id": "C1",
                    "warrant_reconstruction": "Measurements bear on C1.",
                }
            ],
            "terminal_claim_ids_by_question": {"Q1": ["C1"]},
        },
        active_question_ids={"Q1"},
    )
    assert any(
        item.code == "claim_without_argument_attempt" and item.target_id == "C2"
        for item in issues
    )


def test_indirect_dependency_cycle_fails():
    graph = {
        "claims": [_claim("C1"), _claim("C2")],
        "arguments": [
            {
                "id": "A1",
                "premise_claim_ids": ["C2"],
                "conclusion_claim_id": "C1",
                "warrant_reconstruction": "C2 implies C1.",
            },
            {
                "id": "A2",
                "premise_claim_ids": ["C1"],
                "conclusion_claim_id": "C2",
                "warrant_reconstruction": "C1 implies C2.",
            },
        ],
        "terminal_claim_ids_by_question": {"Q1": ["C1"]},
    }
    issues = validate_graph_skeleton(graph, active_question_ids={"Q1"})
    assert "dependency_cycle" in {item.code for item in issues}


def test_defeater_requires_claim_premise_as_visible_origin():
    graph = {
        "claims": [_claim("C1")],
        "arguments": [
            {
                "id": "A1",
                "anticipated_ground_kinds": ["measurement"],
                "conclusion_claim_id": "C1",
                "warrant_reconstruction": "Measurements bear on C1.",
            }
        ],
        "defeaters": [
            {
                "id": "D1",
                "target_id": "A1",
                "premise_claim_ids": [],
            }
        ],
        "terminal_claim_ids_by_question": {"Q1": ["C1"]},
    }
    issues = validate_graph_skeleton(graph, active_question_ids={"Q1"})
    assert "defeater_without_premise_claim" in {
        item.code for item in issues
    }


def test_projection_contract_rejects_ad_hoc_card_assessment():
    graph = {
        "claims": [
            {
                "id": "C1",
                "proposition": "C1",
                "display_assessment": {
                    "evidential_state": "insufficient",
                    "acceptance_status": "supported",
                    "coverage_state": "limited",
                    "coverage_display": {
                        "harvey_quarters": 4,
                        "scale_quarters": 4,
                    },
                },
            }
        ],
        "arguments": [
            {
                "id": "A1",
                "anticipated_ground_kinds": ["measurement"],
                "conclusion_claim_id": "C1",
                "warrant_reconstruction": "Measurements bear on C1.",
            }
        ],
        "defeaters": [],
        "terminal_claim_ids_by_question": {"Q1": ["C1"]},
        "projection_contract": {
            "coverage_harvey_mapping": {
                "not_assessed": 0,
                "limited": 1,
                "adequate": 4,
                "scale_quarters": 4,
            }
        },
    }
    issues = validate_graph_skeleton(graph, active_question_ids={"Q1"})
    codes = {item.code for item in issues}
    assert "invalid_projection_acceptance" in codes
    assert "invalid_projection_coverage_display" in codes


def test_reachability_reports_multihop_grounded_route():
    graph = {
        "claims": [_claim("C1"), _claim("C2"), _claim("C3")],
        "arguments": [
            {
                "id": "A1",
                "ground_ids": ["G1"],
                "premise_claim_ids": [],
                "conclusion_claim_id": "C1",
            },
            {
                "id": "A2",
                "ground_ids": [],
                "premise_claim_ids": ["C1"],
                "conclusion_claim_id": "C2",
            },
            {
                "id": "A3",
                "ground_ids": [],
                "premise_claim_ids": ["C2"],
                "conclusion_claim_id": "C3",
            },
        ],
        "defeaters": [],
        "terminal_claim_ids_by_question": {"Q1": ["C3"]},
    }
    report = inferential_reachability_report(
        graph, active_question_ids={"Q1"}
    )
    assert report["structurally_connected"]
    assert report["claims_reaching_a_terminal"] == 3
    assert report["maximum_claim_dependency_depth"] == 3
    assert report["terminal_claim_ids_without_complete_ground_route"] == []


def test_reachability_preserves_explicitly_missing_support():
    graph = {
        "claims": [_claim("C1"), _claim("C2")],
        "arguments": [
            {
                "id": "A1",
                "ground_ids": [],
                "premise_claim_ids": [],
                "anticipated_ground_kinds": ["deployment control test"],
                "conclusion_claim_id": "C1"
            },
            {
                "id": "A2",
                "ground_ids": [],
                "premise_claim_ids": ["C1"],
                "conclusion_claim_id": "C2",
            },
        ],
        "defeaters": [],
        "terminal_claim_ids_by_question": {"Q1": ["C2"]},
    }
    report = inferential_reachability_report(
        graph, active_question_ids={"Q1"}
    )
    assert report["structurally_connected"]
    assert report["terminal_claim_ids_without_complete_ground_route"] == ["C2"]
