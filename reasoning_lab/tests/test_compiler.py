from p2d_reasoning_lab.compiler import compile_reasoning_artifact


def _claim(identifier: str, proposition: str) -> dict:
    return {
        "id": identifier,
        "proposition": proposition,
        "polarity": "positive",
        "modality": "defeasible",
        "conditions": [],
        "temporal_scope": "",
        "comparison_class": "",
        "operationalization": "",
        "question_ids": ["Q1"],
        "source_research_claim_ids": [identifier],
        "valence_assessments": [
            {
                "id": f"VA-{identifier}",
                "producer": "fixture",
                "credence": 0.7,
                "reliability": 1.0,
                "independence_group": f"fixture:{identifier}",
                "calibration_state": "uncalibrated",
            }
        ],
    }


def test_compiler_runs_real_solver_and_builds_projection() -> None:
    graph = {
        "claims": [_claim("C1", "P"), _claim("C2", "Q")],
        "arguments": [
            {
                "id": "A1",
                "premise_claim_ids": [],
                "ground_ids": ["G1"],
                "conclusion_claim_id": "C1",
                "warrant_reconstruction": "The direct observation supports P.",
                "assessment": "strong",
                "formal_candidate": {"suitable": False, "fidelity": "unsuitable"},
            },
            {
                "id": "A2",
                "premise_claim_ids": ["C1"],
                "ground_ids": [],
                "conclusion_claim_id": "C2",
                "warrant_reconstruction": "P and P implies Q entail Q.",
                "assessment": "strong",
                "formal_candidate": {
                    "suitable": True,
                    "premises": ["implies(P, Q)", "P"],
                    "conclusion": "Q",
                    "fidelity": "exact_for_stated_scope",
                },
            },
        ],
        "defeaters": [],
        "terminal_claim_ids_by_question": {"Q1": ["C2"]},
    }
    lane = {
        "direction": "support",
        "searches_run": ["fixture"],
        "grounds": [{"id": "G1", "url": "https://example.test"}],
        "observed_saturation": "no",
    }
    compiled = compile_reasoning_artifact(
        graph=graph,
        portfolio={
            "questions": [{"id": "Q1", "disposition": "active"}]
        },
        research={
            "C1": {"lanes": [lane]},
            "C2": {"lanes": [lane]},
        },
        grounds=[
            {
                "id": "G1",
                "url": "https://example.test",
                "directness": "direct",
                "source_type": "primary",
            }
        ],
        artifact_id="fixture",
    )
    assert compiled["formal_validation"]["formal_candidates_checked"] == 1
    result = compiled["formal_validation"]["results"][0]["result"]
    assert result["z3"]["status"] == "proved"
    assert result["truth_table"]["entailed"] is True
    assert {item["claim_id"] for item in compiled["visual_projection"]["cards"]} == {
        "C1",
        "C2",
    }
