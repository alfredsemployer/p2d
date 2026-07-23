"""Deterministic selection of model-proposed inquiry questions."""

from __future__ import annotations

from typing import Any


SUPPORTED_TYPES = {
    "proposition",
    "comparative",
    "descriptive_magnitude",
    "interpretive",
    "normative",
    "decision",
}
SPECIALIZED_TYPES = {"predictive", "causal", "explanatory"}
RANKING_FIELDS = (
    "relevance",
    "importance",
    "leverage",
    "answerability",
    "novelty",
    "diversity",
)


def rank_questions(
    questions: list[dict[str, Any]], *, active_limit: int = 3
) -> list[dict[str, Any]]:
    """Rank candidates reproducibly while preserving discarded alternatives."""

    if active_limit < 1:
        raise ValueError("active_limit must be positive")
    rows: list[dict[str, Any]] = []
    for index, question in enumerate(questions):
        item = dict(question)
        question_type = str(item.get("type") or "proposition")
        ranking = dict(item.get("ranking") or {})
        scores = {
            field: max(0.0, min(10.0, float(ranking.get(field, 0.0))))
            for field in RANKING_FIELDS
        }
        score = (
            0.25 * scores["relevance"]
            + 0.23 * scores["importance"]
            + 0.20 * scores["leverage"]
            + 0.17 * scores["answerability"]
            + 0.10 * scores["novelty"]
            + 0.05 * scores["diversity"]
        )
        specialized = question_type in SPECIALIZED_TYPES
        unsupported = question_type not in SUPPORTED_TYPES | SPECIALIZED_TYPES
        item["ranking"] = scores
        item["selection_score"] = round(score, 6)
        item["_original_index"] = index
        if specialized:
            item["disposition"] = "requires_specialized_pipeline"
            item["disposition_reason"] = (
                f"{question_type} questions require a specialized pipeline"
            )
        elif unsupported:
            item["disposition"] = "currently_unanswerable"
            item["disposition_reason"] = (
                f"question type {question_type!r} is not in the governed vocabulary"
            )
        rows.append(item)

    eligible = [
        item
        for item in rows
        if item.get("disposition")
        not in {"requires_specialized_pipeline", "currently_unanswerable"}
    ]
    eligible.sort(
        key=lambda item: (
            -float(item["selection_score"]),
            int(item["_original_index"]),
        )
    )
    selected_ids = {
        str(item.get("id") or "") for item in eligible[:active_limit]
    }
    output: list[dict[str, Any]] = []
    for item in rows:
        identifier = str(item.get("id") or "")
        if item.get("disposition") not in {
            "requires_specialized_pipeline",
            "currently_unanswerable",
        }:
            if identifier in selected_ids:
                item["disposition"] = "active"
                item["disposition_reason"] = "selected by inquiry-ranking-v1"
            else:
                item["disposition"] = "deferred"
                item["disposition_reason"] = (
                    "ranked below this run's active-question limit"
                )
        item["selection_policy"] = "inquiry-ranking-v1"
        item.pop("_original_index", None)
        output.append(item)
    return output
