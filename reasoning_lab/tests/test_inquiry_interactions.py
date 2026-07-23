import pytest

from p2d_reasoning_lab.inquiry import rank_questions
from p2d_reasoning_lab.interactions import (
    make_interaction_record,
    validate_interaction_transition,
)


def test_predictive_question_is_routed_to_specialized_pipeline() -> None:
    questions = [
        {
            "id": "Q1",
            "type": "predictive",
            "ranking": {"relevance": 10, "importance": 10},
        },
        {
            "id": "Q2",
            "type": "comparative",
            "ranking": {"relevance": 8, "importance": 8},
        },
    ]
    ranked = rank_questions(questions, active_limit=1)
    assert ranked[0]["disposition"] == "requires_specialized_pipeline"
    assert ranked[1]["disposition"] == "active"


def test_interaction_is_append_only_proposal() -> None:
    record = make_interaction_record(
        kind="challenge",
        artifact_id="run-1",
        target_id="C1",
        request="Test the contrary evidence.",
        created_at="2026-07-23T12:00:00+00:00",
    )
    assert record["status"] == "proposed"
    assert "never silently changes" in record["mutation_policy"]
    running = {**record, "status": "running"}
    validate_interaction_transition(record, running)
    with pytest.raises(ValueError):
        validate_interaction_transition(record, {**record, "status": "completed"})
