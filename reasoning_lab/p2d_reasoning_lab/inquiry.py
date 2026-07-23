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


def validate_discourse_map(record: dict[str, Any]) -> list[str]:
    """Validate local question/hypothesis linkage within one discourse pass."""

    errors: list[str] = []
    questions = list(record.get("questions") or [])
    question_keys = [str(item.get("local_id") or "") for item in questions]
    if not questions:
        errors.append("discourse map contains no questions")
    if not all(question_keys):
        errors.append("every discourse question requires a local_id")
    if len(question_keys) != len(set(question_keys)):
        errors.append("discourse question local_ids must be unique")
    known = set(question_keys)
    for relation in record.get("question_relations") or []:
        source = str(relation.get("source_question_local_id") or "")
        target = str(relation.get("target_question_local_id") or "")
        if source not in known or target not in known:
            errors.append(
                "question relation references an unknown local question"
            )
        if source == target:
            errors.append("question relation cannot be self-referential")
    hypotheses = list(record.get("hypotheses") or [])
    for item in hypotheses:
        identifier = str(item.get("local_id") or "")
        if not identifier:
            errors.append("every discourse hypothesis requires a local_id")
        linked = set(str(value) for value in item.get("question_local_ids") or [])
        if not linked:
            errors.append(f"hypothesis {identifier or '<unknown>'} is not linked to a question")
        unknown = linked - known
        if unknown:
            errors.append(
                f"hypothesis {identifier or '<unknown>'} references unknown questions: "
                + ", ".join(sorted(unknown))
            )
    return errors


def validate_question_map(record: dict[str, Any]) -> list[str]:
    """Validate the inquiry-layer graph, including meta-question structure."""

    errors: list[str] = []
    questions = list(record.get("questions") or [])
    audit = record.get("meta_question_audit")
    if not isinstance(audit, dict):
        errors.append("question map has no meta_question_audit")
    else:
        for field in (
            "broader_outcomes_considered",
            "proxy_substitutions_avoided",
            "missing_meta_questions",
        ):
            if field not in audit:
                errors.append(f"meta_question_audit is missing {field}")
    known = {str(item.get("id") or "") for item in questions}
    permitted_levels = {"object", "meta", "bridge"}
    for question in questions:
        identifier = str(question.get("id") or "")
        level = str(question.get("question_level") or "")
        if level not in permitted_levels:
            errors.append(
                f"question {identifier or '<unknown>'} has invalid question_level"
            )
        if not str(question.get("why_it_matters") or "").strip():
            errors.append(
                f"question {identifier or '<unknown>'} has no why_it_matters"
            )
    permitted_relations = {
        "decomposes_into",
        "depends_on",
        "operationalizes",
        "changes_interpretation_of",
        "counterbalances",
    }
    relation_keys: set[tuple[str, str, str]] = set()
    for relation in record.get("question_relations") or []:
        source = str(relation.get("source_question_id") or "")
        target = str(relation.get("target_question_id") or "")
        kind = str(relation.get("relation") or "")
        if source not in known or target not in known:
            errors.append("question relation references an unknown question")
        if source == target:
            errors.append("question relation cannot be self-referential")
        if kind not in permitted_relations:
            errors.append(f"invalid question relation: {kind or '<missing>'}")
        key = (source, kind, target)
        if key in relation_keys:
            errors.append("duplicate question relation")
        relation_keys.add(key)
    meta_ids = {
        str(item.get("id"))
        for item in questions
        if item.get("question_level") == "meta"
    }
    for meta_id in meta_ids:
        has_dependency = any(
            relation.get("source_question_id") == meta_id
            and relation.get("relation") in {"decomposes_into", "depends_on"}
            for relation in record.get("question_relations") or []
        )
        if not has_dependency:
            errors.append(
                f"meta question {meta_id} has no decomposes_into or depends_on relation"
            )
    return errors


def validate_hypothesis_portfolio(
    portfolio: dict[str, Any],
    *,
    active_question_ids: set[str],
    minimum_per_question: int = 2,
) -> list[str]:
    """Require candidate answers to remain typed and linked to questions."""

    errors: list[str] = []
    hypotheses = list(portfolio.get("hypotheses") or [])
    known_questions = {
        str(item.get("id") or "") for item in portfolio.get("questions") or []
    }
    counts = {question_id: 0 for question_id in active_question_ids}
    seen_ids: set[str] = set()
    for hypothesis in hypotheses:
        identifier = str(hypothesis.get("id") or "")
        if not identifier:
            errors.append("every hypothesis requires an id")
        elif identifier in seen_ids:
            errors.append(f"duplicate hypothesis id: {identifier}")
        seen_ids.add(identifier)
        links = set(
            str(item) for item in hypothesis.get("question_ids") or []
        )
        if not links:
            errors.append(f"hypothesis {identifier or '<unknown>'} has no question_ids")
        unknown = links - known_questions
        if unknown:
            errors.append(
                f"hypothesis {identifier or '<unknown>'} references unknown questions: "
                + ", ".join(sorted(unknown))
            )
        for question_id in links & active_question_ids:
            counts[question_id] += 1
        if not str(hypothesis.get("candidate_answer") or "").strip():
            errors.append(
                f"hypothesis {identifier or '<unknown>'} has no candidate_answer"
            )
        if not hypothesis.get("falsifiers"):
            errors.append(
                f"hypothesis {identifier or '<unknown>'} has no falsifiers"
            )
        if not hypothesis.get("generation_provenance"):
            errors.append(
                f"hypothesis {identifier or '<unknown>'} has no generation provenance"
            )
    for question_id, count in counts.items():
        if count < minimum_per_question:
            errors.append(
                f"active question {question_id} has {count} hypotheses; "
                f"minimum is {minimum_per_question}"
            )
    return errors


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
