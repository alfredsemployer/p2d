"""Build a connected post-run argument graph from existing run artifacts."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .validation import (
    inferential_reachability_report,
    validate_graph_skeleton,
)


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _claim(
    identifier: str,
    proposition: str,
    *,
    questions: list[str],
    roles: list[str],
    state: str,
    source_claim_ids: list[str],
    modality: str = "defeasible",
) -> dict[str, Any]:
    acceptance_status = (
        "supported" if state == "supported" else "not_supported"
    )
    return {
        "id": identifier,
        "version": 1,
        "proposition": proposition,
        "modality": modality,
        "question_ids": questions,
        "roles": roles,
        "load_bearing": True,
        "display_assessment": {
            "evidential_state": state,
            "acceptance_status": acceptance_status,
            "coverage_state": "limited",
            "coverage_display": {
                "label": "limited",
                "harvey_quarters": 1,
                "scale_quarters": 4,
                "mapping_version": "coverage-harvey-v0.1",
            },
            "acceptance_rule": (
                "supported iff evidential_state is supported; otherwise "
                "not_supported under the active acceptance policy"
            ),
            "derivation": "post-run reconstruction from existing grounds and assessments",
            "source_claim_assessment_ids": source_claim_ids,
            "independent_review_status": "pending",
        },
    }


def _argument(
    identifier: str,
    conclusion: str,
    *,
    premises: list[str] | None = None,
    grounds: list[str] | None = None,
    anticipated: list[str] | None = None,
    inference_type: str,
    scheme: str,
    warrant: str,
    assessment: str,
    assumptions: list[str] | None = None,
    exceptions: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "id": identifier,
        "version": 1,
        "premise_claim_ids": premises or [],
        "ground_ids": grounds or [],
        "anticipated_ground_kinds": anticipated or [],
        "conclusion_claim_id": conclusion,
        "inference_type": inference_type,
        "scheme": scheme,
        "warrant_reconstruction": warrant,
        "warrant_fidelity": "plausible_reconstruction",
        "strictness": "defeasible",
        "assumptions": assumptions or [],
        "exceptions": exceptions or [],
        "critical_questions": [],
        "assessment": assessment,
        "formal_candidate": {
            "suitable": False,
            "reason": (
                "This is a defeasible empirical or practical inference, not a "
                "strict propositional consequence."
            ),
            "premises": [],
            "conclusion": "",
            "fidelity": "unsuitable",
        },
    }


def build_reconstructed_graph(run_dir: str | Path) -> dict[str, Any]:
    root = Path(run_dir)
    portfolio = _load(root / "question_portfolio.json")
    grounds = _load(root / "normalized_grounds.json")
    known_ground_ids = {item["id"] for item in grounds}
    active_question_ids = {
        item["id"]
        for item in portfolio["questions"]
        if item.get("disposition") == "active"
    }

    claims = [
        _claim(
            "RC1",
            (
                "On several named agentic and knowledge-work evaluations, "
                "Kimi K3 matched or exceeded some leading hosted alternatives."
            ),
            questions=["Q1", "Q2"],
            roles=["intermediate empirical summary"],
            state="supported",
            source_claim_ids=["C2"],
        ),
        _claim(
            "RC2",
            (
                "Kimi K3 is competitive with at least some leading "
                "alternatives on at least one high-value workflow."
            ),
            questions=["Q1", "Q2", "Q3"],
            roles=["Q1 terminal", "shared capability premise"],
            state="supported",
            source_claim_ids=["C2"],
        ),
        _claim(
            "RC3",
            (
                "Kimi K3's improvement over preceding Kimi models is "
                "established by independently reproducible, matched evaluations."
            ),
            questions=["Q1"],
            roles=["comparative hinge"],
            state="insufficient",
            source_claim_ids=["C1"],
        ),
        _claim(
            "RC4",
            (
                "Kimi K3 demonstrates broad capability superiority over "
                "preceding Kimi models and leading alternatives."
            ),
            questions=["Q1"],
            roles=["Q1 terminal"],
            state="insufficient",
            source_claim_ids=["C1", "C2"],
        ),
        _claim(
            "RC5",
            (
                "Kimi K3 reliably uses its reported long context for retrieval "
                "and reasoning across relevant tasks."
            ),
            questions=["Q1"],
            roles=["Q1 terminal"],
            state="insufficient",
            source_claim_ids=["C1", "C3"],
        ),
        _claim(
            "RC6",
            (
                "Large advertised context capacity does not by itself "
                "establish reliable long-context performance."
            ),
            questions=["Q1"],
            roles=["defeater backing", "methodological hinge"],
            state="supported",
            source_claim_ids=["C3"],
        ),
        _claim(
            "RC7",
            (
                "Kimi K3 had lower monetary cost than selected comparators on "
                "some evaluated tasks."
            ),
            questions=["Q2"],
            roles=["Q2 terminal", "cost premise"],
            state="supported",
            source_claim_ids=["C2", "C4"],
        ),
        _claim(
            "RC8",
            (
                "Kimi K3 has a lower total quality-adjusted cost per successful "
                "task across relevant workloads."
            ),
            questions=["Q2"],
            roles=["Q2 terminal"],
            state="insufficient",
            source_claim_ids=["C4"],
        ),
        _claim(
            "RC9",
            (
                "Hosted Kimi K3 and any downloadable checkpoint are materially "
                "different deployment and governance options."
            ),
            questions=["Q2"],
            roles=["Q2 terminal", "Q3 context"],
            state="supported",
            source_claim_ids=["C5"],
            modality="conditional",
        ),
        _claim(
            "RC10",
            (
                "Kimi K3's latency, correction burden, and deployment costs "
                "are material constraints not captured by token price alone."
            ),
            questions=["Q1", "Q2"],
            roles=["defeater backing", "total-cost hinge"],
            state="supported",
            source_claim_ids=["C4"],
        ),
        _claim(
            "RC11",
            (
                "Available reports identify hallucination, over-initiative, "
                "and runtime-instability risks for Kimi K3."
            ),
            questions=["Q3"],
            roles=["defeater backing", "risk premise"],
            state="supported",
            source_claim_ids=["C6"],
        ),
        _claim(
            "RC12",
            (
                "Tested controls keep Kimi K3's operational risks within a "
                "deploying institution's tolerance."
            ),
            questions=["Q3"],
            roles=["control-effectiveness premise"],
            state="insufficient",
            source_claim_ids=["C6"],
        ),
        _claim(
            "RC13",
            (
                "Kimi K3 is suitable for minimally supervised long-horizon "
                "workflows."
            ),
            questions=["Q3"],
            roles=["Q3 terminal"],
            state="insufficient",
            source_claim_ids=["C6"],
        ),
        _claim(
            "RC14",
            (
                "The cited evidence does not include a public independent "
                "replication of Kimi K3 under a complete matched protocol."
            ),
            questions=["Q1"],
            roles=["defeater backing", "reproducibility constraint"],
            state="supported",
            source_claim_ids=["C1"],
        ),
        _claim(
            "RC15",
            (
                "The cited evaluations show mixed performance on selected "
                "workflows rather than broad capability superiority."
            ),
            questions=["Q1"],
            roles=["defeater backing", "scope constraint"],
            state="supported",
            source_claim_ids=["C2"],
        ),
        _claim(
            "RC16",
            (
                "As of the run date, Kimi K3 checkpoint release and final "
                "license terms had not been verified."
            ),
            questions=["Q2"],
            roles=["defeater backing", "availability constraint"],
            state="supported",
            source_claim_ids=["C5"],
        ),
    ]

    arguments = [
        _argument(
            "RA1",
            "RC1",
            grounds=[
                "G-C2-support-1",
                "G-C2-support-2",
                "G-C2-support-3",
                "G-C2-support-5",
            ],
            inference_type="enumerative_inductive",
            scheme="argument_from_multiple_evaluations",
            warrant=(
                "Results on several evaluations designed to sample agentic and "
                "knowledge-work tasks are evidence about performance on those "
                "evaluated workflows, without establishing general superiority."
            ),
            assessment="moderate",
        ),
        _argument(
            "RA2",
            "RC2",
            premises=["RC1"],
            inference_type="classificatory",
            scheme="threshold_classification",
            warrant=(
                "Matching or exceeding leading alternatives on at least one "
                "high-value evaluated workflow is sufficient for the narrow "
                "classification 'competitive on at least one workflow'."
            ),
            assessment="moderate",
            exceptions=[
                "The evaluations may not represent deployed workflow conditions."
            ],
        ),
        _argument(
            "RA3",
            "RC3",
            grounds=["G-C1-support-1", "G-C1-challenge-4"],
            inference_type="inductive",
            scheme="argument_from_reported_comparison",
            warrant=(
                "A reported same-task score difference can support a capability "
                "difference only if the protocol and result are independently "
                "reproducible under matched conditions."
            ),
            assessment="weak",
        ),
        _argument(
            "RA4",
            "RC4",
            premises=["RC2", "RC3"],
            inference_type="inductive",
            scheme="generalization_from_comparative_evidence",
            warrant=(
                "Workflow-specific competitiveness plus reproducible gains over "
                "prior models would support a broader superiority claim only if "
                "the evaluations cover the relevant capability profile."
            ),
            assessment="weak",
            assumptions=[
                "The evaluated tasks adequately represent the broader capability profile."
            ],
        ),
        _argument(
            "RA5",
            "RC5",
            grounds=["G-C1-support-4"],
            inference_type="inductive",
            scheme="generalization_from_first_hand_test",
            warrant=(
                "Accurate retrieval in a large-context test is some evidence of "
                "usable long-context behavior, but one test does not establish "
                "reliability across tasks and conditions."
            ),
            assessment="weak",
        ),
        _argument(
            "RA6",
            "RC6",
            grounds=[
                "G-C3-support-1",
                "G-C3-support-3",
                "G-C3-challenge-3",
                "G-C3-challenge-4",
            ],
            inference_type="enumerative_inductive",
            scheme="argument_from_controlled_studies",
            warrant=(
                "Observed degradation within advertised context limits, "
                "including with successful retrieval, shows that nominal "
                "capacity alone is not sufficient evidence of reliability."
            ),
            assessment="strong",
        ),
        _argument(
            "RA7",
            "RC7",
            grounds=[
                "G-C4-challenge-1",
                "G-C4-challenge-2",
                "G-C4-challenge-3",
            ],
            inference_type="comparative_quantitative",
            scheme="argument_from_observed_task_cost",
            warrant=(
                "Lower measured monetary cost on matched selected tasks supports "
                "a claim about those tasks, not about all-in cost across workloads."
            ),
            assessment="moderate",
        ),
        _argument(
            "RA8",
            "RC8",
            premises=["RC7"],
            inference_type="practical",
            scheme="price_to_total_cost",
            warrant=(
                "Lower monetary cost on selected tasks would indicate lower "
                "quality-adjusted total cost only if latency, reliability, "
                "hardware, and correction burdens are also favorable."
            ),
            assessment="weak",
        ),
        _argument(
            "RA9",
            "RC9",
            grounds=[
                "G-C5-support-1",
                "G-C5-support-2",
                "G-C5-support-3",
                "G-C5-support-4",
                "G-C5-support-5",
                "G-C5-support-6",
            ],
            inference_type="classificatory",
            scheme="deployment_mode_comparison",
            warrant=(
                "Material differences in availability, hardware, data handling, "
                "customization, licensing, and cost structure make hosted access "
                "and a downloadable checkpoint distinct deployment objects."
            ),
            assessment="moderate",
        ),
        _argument(
            "RA10",
            "RC10",
            grounds=[
                "G-C4-support-4",
                "G-C4-support-6",
                "G-C4-challenge-1",
                "G-C4-challenge-4",
            ],
            inference_type="inductive",
            scheme="argument_from_operational_constraints",
            warrant=(
                "Observed latency and hallucination differences, together with "
                "unmeasured correction burden, are material to total task cost "
                "even when token or task price is lower."
            ),
            assessment="moderate",
        ),
        _argument(
            "RA11",
            "RC11",
            grounds=[
                "G-C6-support-1",
                "G-C6-support-2",
                "G-C6-support-4",
                "G-C6-challenge-4",
            ],
            inference_type="inductive",
            scheme="argument_from_reported_failure_modes",
            warrant=(
                "Independent measurements and vendor warnings about fabrication, "
                "unexpected actions, and state sensitivity establish that these "
                "are live deployment risks requiring evaluation."
            ),
            assessment="moderate",
        ),
        _argument(
            "RA12",
            "RC12",
            anticipated=[
                "deployment-specific red-team results",
                "control-effectiveness measurements",
                "institution-specific risk thresholds",
            ],
            inference_type="practical",
            scheme="control_effectiveness_assessment",
            warrant=(
                "Suitability requires evidence that specified controls reduce "
                "observed risks below the deploying institution's thresholds."
            ),
            assessment="unresolved",
        ),
        _argument(
            "RA13",
            "RC13",
            premises=["RC2", "RC12"],
            inference_type="practical",
            scheme="capability_plus_controlled_risk",
            warrant=(
                "A capable model is suitable for minimally supervised long-horizon "
                "work only when tested controls keep its operational risks within "
                "the institution's tolerance."
            ),
            assessment="unresolved",
        ),
        _argument(
            "RA14",
            "RC14",
            grounds=["G-C1-challenge-4"],
            inference_type="inductive",
            scheme="argument_from_missing_independent_result",
            warrant=(
                "The absence of a K3 result from an available independent "
                "comparison, together with the run's lack of a complete matched "
                "replication, supports the bounded claim that such replication "
                "was not present in the cited evidence."
            ),
            assessment="moderate",
        ),
        _argument(
            "RA15",
            "RC15",
            grounds=["G-C2-support-1", "G-C2-support-5"],
            inference_type="inductive",
            scheme="argument_from_mixed_comparative_results",
            warrant=(
                "Results that place K3 ahead of some comparators and behind "
                "others on selected evaluations support a mixed, scoped "
                "performance conclusion rather than broad superiority."
            ),
            assessment="moderate",
        ),
        _argument(
            "RA16",
            "RC16",
            grounds=["G-C5-support-1", "G-C5-support-3"],
            inference_type="temporal",
            scheme="argument_from_release_status",
            warrant=(
                "A scheduled future weight release and unpublished final license "
                "terms establish that checkpoint availability and licensing were "
                "not verified as of the run's evidence boundary."
            ),
            assessment="moderate",
        ),
    ]

    defeaters = [
        {
            "id": "RD1",
            "target_type": "argument",
            "target_id": "RA2",
            "attack_type": "undercutter",
            "premise_claim_ids": ["RC10"],
            "ground_ids": ["G-C2-challenge-2"],
            "content": (
                "A large latency penalty and differing harnesses can make benchmark "
                "parity less informative about practical competitiveness."
            ),
            "status": "contested",
        },
        {
            "id": "RD2",
            "target_type": "argument",
            "target_id": "RA3",
            "attack_type": "undercutter",
            "premise_claim_ids": ["RC14"],
            "ground_ids": [],
            "content": (
                "The available evidence does not supply a public independent "
                "replication with a complete matched protocol."
            ),
            "status": "supported",
        },
        {
            "id": "RD3",
            "target_type": "argument",
            "target_id": "RA4",
            "attack_type": "undercutter",
            "premise_claim_ids": ["RC15"],
            "ground_ids": [],
            "content": (
                "K3 trails leading alternatives on some evaluations, and the "
                "sampled workflows do not cover general capability."
            ),
            "status": "supported",
        },
        {
            "id": "RD4",
            "target_type": "argument",
            "target_id": "RA5",
            "attack_type": "undercutter",
            "premise_claim_ids": ["RC6"],
            "ground_ids": [],
            "content": (
                "General controlled studies show that long context capacity and "
                "successful retrieval can coexist with degraded reasoning."
            ),
            "status": "supported",
        },
        {
            "id": "RD5",
            "target_type": "argument",
            "target_id": "RA8",
            "attack_type": "undercutter",
            "premise_claim_ids": ["RC10"],
            "ground_ids": [],
            "content": (
                "Latency, correction burden, and deployment costs block the move "
                "from lower selected-task price to lower total cost."
            ),
            "status": "supported",
        },
        {
            "id": "RD6",
            "target_type": "argument",
            "target_id": "RA9",
            "attack_type": "exception",
            "premise_claim_ids": ["RC16"],
            "ground_ids": [],
            "content": (
                "As of the run date, checkpoint release and final license terms "
                "were not verified; checkpoint-side conclusions remain conditional."
            ),
            "status": "supported",
        },
        {
            "id": "RD7",
            "target_type": "argument",
            "target_id": "RA13",
            "attack_type": "undercutter",
            "premise_claim_ids": ["RC11"],
            "ground_ids": [],
            "content": (
                "Reported hallucination, over-initiative, and instability remain "
                "unresolved risks for minimally supervised deployment."
            ),
            "status": "supported",
        },
    ]

    graph = {
        "schema_version": "0.3-reconstruction",
        "generated_at": datetime.now(UTC).isoformat(),
        "source_run": str(root),
        "source_artifacts": [
            "normalized_grounds.json",
            "claim_assessments.json",
            "question_portfolio.json",
        ],
        "status": (
            "Post-run inferential reconstruction. Uses no new research. New "
            "claim assessments require independent review."
        ),
        "projection_contract": {
            "id": "answer-first-claim-graph",
            "version": "0.1.0",
            "question_heading": "question_portfolio active question text",
            "card_rule": (
                "Render every claim in the terminal dependency closure, including "
                "claims that back defeaters; never render grounds or arguments as cards."
            ),
            "designation_precedence": ["answer", "challenge", "support"],
            "designation_rules": {
                "answer": "claim is terminal for the active question",
                "challenge": (
                    "claim is a premise of a defeater targeting an included argument"
                ),
                "support": "other claim in the terminal dependency closure",
            },
            "relationship_rules": {
                "support": "solid orthogonal line for an Argument premise",
                "challenge": "dashed red orthogonal line for a Defeater premise",
                "grounds": "shown only in claim or relationship inspection",
            },
            "column_rule": (
                "answer-first distance from a terminal over support and defeater-backing edges"
            ),
            "acceptance_status_field": "display_assessment.acceptance_status",
            "acceptance_rule": (
                "supported iff evidential_state is supported; all other assessed "
                "states map to not_supported without implying falsity"
            ),
            "coverage_field": "display_assessment.coverage_state",
            "coverage_harvey_mapping": {
                "not_assessed": 0,
                "limited": 1,
                "adequate": 4,
                "scale_quarters": 4,
            },
        },
        "claims": claims,
        "arguments": arguments,
        "defeaters": defeaters,
        "terminal_claim_ids_by_question": {
            "Q1": ["RC2", "RC4", "RC5"],
            "Q2": ["RC7", "RC8", "RC9"],
            "Q3": ["RC13"],
        },
    }
    issues = validate_graph_skeleton(
        graph,
        active_question_ids=active_question_ids,
        known_ground_ids=known_ground_ids,
    )
    graph["structural_validation"] = [item.to_dict() for item in issues]
    graph["inferential_reachability"] = inferential_reachability_report(
        graph,
        active_question_ids=active_question_ids,
    )
    _save(root / "argument_graph_reconstructed.json", graph)

    answer = _load(root / "answer_bundle_revised.json")
    terminal_map = graph["terminal_claim_ids_by_question"]
    for verdict in answer.get("question_verdicts", []):
        verdict["claim_ids"] = terminal_map.get(verdict["question_id"], [])
    answer["_graph_projection"] = {
        "graph_artifact": "argument_graph_reconstructed.json",
        "mapping_method": "deterministic terminal-claim remap",
        "independent_review_status": "pending",
        "prose_unchanged_from_independently_audited_answer": True,
    }
    _save(root / "answer_bundle_reconstructed.json", answer)
    return graph
