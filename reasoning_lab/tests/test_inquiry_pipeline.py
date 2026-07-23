from types import SimpleNamespace

from p2d_reasoning_lab.pipeline import PipelineRun
from p2d_reasoning_lab.verdict import VerdictPolicy


class FakeInquiryClient:
    def __init__(self) -> None:
        self.prompts: dict[str, list[str]] = {}

    def call_json(self, *, purpose: str, prompt: str, model: str, **_: object):
        self.prompts.setdefault(purpose, []).append(prompt)
        reply = SimpleNamespace(model=model, response_id=f"reply:{purpose}")
        if purpose == "question_synthesis":
            return (
                {
                    "answer_contract": {"referent": "rent control"},
                    "neutral_context_summary": "A housing policy changes allocation.",
                    "key_term_definitions": [],
                    "questions": [
                        {
                            "id": "Q1",
                            "question": "Does rent control reduce listed rental supply?",
                            "type": "proposition",
                            "question_level": "object",
                            "why_it_matters": "Supply may affect access.",
                            "resolution_criteria": ["Estimate listed units."],
                            "ranking": {
                                "relevance": 9,
                                "importance": 8,
                                "leverage": 9,
                                "answerability": 8,
                                "novelty": 5,
                                "diversity": 5,
                            },
                            "source_question_refs": ["a:QF1"],
                        },
                        {
                            "id": "Q2",
                            "question": "Does rent control improve effective housing access?",
                            "type": "interpretive",
                            "question_level": "meta",
                            "why_it_matters": "Access is broader than listings.",
                            "resolution_criteria": ["Assess entrants and incumbents."],
                            "ranking": {
                                "relevance": 10,
                                "importance": 10,
                                "leverage": 10,
                                "answerability": 7,
                                "novelty": 8,
                                "diversity": 9,
                            },
                            "source_question_refs": ["b:QF2"],
                        },
                        {
                            "id": "Q3",
                            "question": "How does rent control affect construction?",
                            "type": "comparative",
                            "question_level": "bridge",
                            "why_it_matters": "Construction affects future access.",
                            "resolution_criteria": ["Estimate construction effects."],
                            "ranking": {
                                "relevance": 8,
                                "importance": 8,
                                "leverage": 8,
                                "answerability": 7,
                                "novelty": 6,
                                "diversity": 8,
                            },
                            "source_question_refs": ["c:QF3"],
                        },
                        {
                            "id": "Q4",
                            "question": "What distributional effects occur?",
                            "type": "interpretive",
                            "question_level": "object",
                            "why_it_matters": "Average effects can hide distribution.",
                            "resolution_criteria": ["Compare affected groups."],
                            "ranking": {
                                "relevance": 6,
                                "importance": 7,
                                "leverage": 5,
                                "answerability": 6,
                                "novelty": 5,
                                "diversity": 7,
                            },
                            "source_question_refs": ["a:QF4"],
                        },
                    ],
                    "question_relations": [
                        {
                            "source_question_id": "Q2",
                            "relation": "depends_on",
                            "target_question_id": "Q1",
                        },
                        {
                            "source_question_id": "Q2",
                            "relation": "decomposes_into",
                            "target_question_id": "Q3",
                        },
                    ],
                    "meta_question_audit": {
                        "broader_outcomes_considered": ["effective access"],
                        "proxy_substitutions_avoided": [
                            "listed supply is not effective access"
                        ],
                        "missing_meta_questions": [],
                    },
                },
                reply,
            )
        if purpose.startswith("hypothesis_expansion:"):
            hypotheses = [
                {
                    "local_id": f"HX-{question_id}",
                    "question_ids": [question_id],
                    "candidate_answer": f"Alternative for {question_id}",
                    "falsifiers": ["Contrary observation"],
                }
                for question_id in ("Q1", "Q2", "Q3", "Q4")
            ]
            return ({"question_audits": [], "hypotheses": hypotheses}, reply)
        if purpose == "hypothesis_completion":
            hypotheses = []
            for question_id in ("Q1", "Q2", "Q3"):
                for index in range(3):
                    hypotheses.append(
                        {
                            "id": f"H-{question_id}-{index}",
                            "question_ids": [question_id],
                            "candidate_answer": f"Candidate {index} for {question_id}",
                            "falsifiers": ["Contrary observation"],
                            "alternatives": [],
                            "generation_provenance": ["discourse:a", "expansion:b"],
                        }
                    )
            return (
                {
                    "hypotheses": hypotheses,
                    "deferred_hypothesis_frontier": [],
                    "completion_notes": [],
                },
                reply,
            )
        raise AssertionError(f"unexpected purpose {purpose}")


def _discourse_maps() -> list[dict]:
    return [
        {
            "answer_contract": {},
            "questions": [
                {
                    "local_id": "QF1",
                    "question": "Question?",
                    "why_it_matters": "Reason.",
                }
            ],
            "question_relations": [],
            "hypotheses": [
                {
                    "local_id": "HF1",
                    "question_local_ids": ["QF1"],
                    "candidate_answer": "SECRET_DISCOURSE_HYPOTHESIS",
                }
            ],
            "_provenance": {"discourse_mapper": label},
        }
        for label in ("a", "b", "c")
    ]


def test_inquiry_pipeline_preserves_prompt_blinding_and_object_types(
    tmp_path,
) -> None:
    client = FakeInquiryClient()
    runner = PipelineRun(
        output_dir=tmp_path,
        client=client,  # type: ignore[arg-type]
        question="Does rent control reduce supply, and does that matter?",
        as_of="2026-07-23",
        policy=VerdictPolicy(),
    )
    discourse = _discourse_maps()
    question_map = runner.synthesize_questions(discourse)
    expansions = runner.expand_hypotheses(question_map)
    selected = runner.select_questions(question_map)
    portfolio = runner.complete_hypotheses(selected, discourse, expansions)

    assert "SECRET_DISCOURSE_HYPOTHESIS" not in client.prompts[
        "question_synthesis"
    ][0]
    assert all(
        "SECRET_DISCOURSE_HYPOTHESIS" not in prompt
        for purpose, prompts in client.prompts.items()
        if purpose.startswith("hypothesis_expansion:")
        for prompt in prompts
    )
    assert "SECRET_DISCOURSE_HYPOTHESIS" in client.prompts[
        "hypothesis_completion"
    ][0]
    assert len(
        [
            question
            for question in portfolio["questions"]
            if question["disposition"] == "active"
        ]
    ) == 3
    assert len(portfolio["hypotheses"]) == 9
    assert portfolio["question_relations"][0]["source_question_id"] == "Q2"
    assert len(portfolio["question_audits"]) == 2
