import pytest

from p2d_reasoning_lab.inquiry import (
    rank_questions,
    validate_discourse_map,
    validate_hypothesis_portfolio,
    validate_question_map,
)
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


def test_discourse_hypotheses_must_reference_questions() -> None:
    record = {
        "questions": [{"local_id": "QF1", "question": "Does X change Y?"}],
        "hypotheses": [
            {
                "local_id": "HF1",
                "question_local_ids": ["MISSING"],
                "candidate_answer": "Yes.",
            }
        ],
    }
    errors = validate_discourse_map(record)
    assert any("unknown questions" in item for item in errors)


def test_meta_question_requires_explicit_subquestion_relation() -> None:
    record = {
        "questions": [
            {
                "id": "Q1",
                "question": "Does rent control reduce listed supply?",
                "question_level": "object",
                "why_it_matters": "It may affect access.",
            },
            {
                "id": "Q2",
                "question": "Does the policy improve effective housing access?",
                "question_level": "meta",
                "why_it_matters": "Access is the broader outcome.",
            },
        ],
        "question_relations": [],
        "meta_question_audit": {
            "broader_outcomes_considered": ["effective access"],
            "proxy_substitutions_avoided": ["listed supply is not access"],
            "missing_meta_questions": [],
        },
    }
    assert validate_question_map(record) == [
        "meta question Q2 has no decomposes_into or depends_on relation"
    ]
    record["question_relations"] = [
        {
            "source_question_id": "Q2",
            "relation": "depends_on",
            "target_question_id": "Q1",
        }
    ]
    assert validate_question_map(record) == []


def test_hypotheses_remain_candidate_answers_linked_to_active_question() -> None:
    portfolio = {
        "questions": [{"id": "Q1"}],
        "hypotheses": [
            {
                "id": "H1",
                "question_ids": ["Q1"],
                "candidate_answer": "The effect is negative.",
                "falsifiers": ["A well-identified positive effect."],
                "generation_provenance": ["discourse:a"],
            },
            {
                "id": "H2",
                "question_ids": ["Q1"],
                "candidate_answer": "The measured proxy changes but access does not.",
                "falsifiers": ["A measured access effect."],
                "generation_provenance": ["expansion:b"],
            },
        ],
    }
    assert (
        validate_hypothesis_portfolio(
            portfolio, active_question_ids={"Q1"}
        )
        == []
    )
