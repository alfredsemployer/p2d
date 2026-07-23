"""Post-evidence argument completion and formal-tool reporting."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .budget import BudgetLedger
from .formal import cross_check_propositional
from .openrouter import OpenRouterClient
from .validation import validate_graph_skeleton


ARCHITECT = "openai/gpt-5.6-luna"
CRITIC = "deepseek/deepseek-v3.2"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def normalize_grounds(run_dir: Path) -> list[dict[str, Any]]:
    grounds: list[dict[str, Any]] = []
    for path in sorted((run_dir / "research").glob("C*.json")):
        record = _load(path)
        claim_id = path.stem
        for lane in record.get("lanes", []):
            direction = lane.get("direction", "unknown")
            for index, ground in enumerate(lane.get("grounds") or [], start=1):
                item = dict(ground)
                item["proposed_id"] = item.get("id")
                item["id"] = f"G-{claim_id}-{direction}-{index}"
                item["claim_id"] = claim_id
                item["research_direction"] = direction
                grounds.append(item)
    _save(run_dir / "normalized_grounds.json", grounds)
    return grounds


def _architect_prompt(
    portfolio: dict[str, Any],
    skeleton: dict[str, Any],
    grounds: list[dict[str, Any]],
    assessments: dict[str, Any],
    critic: dict[str, Any] | None = None,
) -> str:
    revision = (
        "\nINDEPENDENT CRITIC FINDINGS TO REPAIR:\n"
        + json.dumps(critic, ensure_ascii=False)
        if critic
        else ""
    )
    return f"""Complete the post-evidence claim-and-argument graph. The prior
decomposition produced Claim vertices but omitted Argument hyperedges. Repair
that structural failure without inventing claims, grounds, or verdicts.

Rules:
- Keep the six existing claims unchanged.
- Every claim must have at least one explicit argument attempt.
- Arguments are hyperedges with premise_claim_ids and/or ground_ids.
- Ground IDs must come from NORMALIZED GROUNDS.
- An argument's failure does not refute its conclusion.
- Model rebutters, underminers, and undercutters as Defeater records, not
  Conflict nodes.
- Warrant text is a warrant_reconstruction with a fidelity assessment.
- Preserve weak and unresolved arguments; do not upgrade them to fill the graph.
- Include a formal_candidate only for an actually strict propositional step.
  Use syntax: and/or/not, implies(P,Q), iff(P,Q), xor(P,Q). Mark fidelity
  candidate_unvalidated unless exactness is independently established.

QUESTION PORTFOLIO:
{json.dumps(portfolio, ensure_ascii=False)}
CLAIM SKELETON:
{json.dumps(skeleton, ensure_ascii=False)}
NORMALIZED GROUNDS:
{json.dumps(grounds, ensure_ascii=False)}
CLAIM ASSESSMENTS:
{json.dumps(assessments, ensure_ascii=False)}
{revision}

Return JSON:
{{
 "claims": [],
 "arguments": [{{
   "id":"A1","premise_claim_ids":[],"ground_ids":[],
   "conclusion_claim_id":"C1","inference_type":"","scheme":"",
   "warrant_reconstruction":"","warrant_fidelity":"faithful|plausible_reconstruction|confabulated|vacuous|unresolved",
   "strictness":"strict|defeasible","assumptions":[],"exceptions":[],
   "critical_questions":[],"assessment":"strong|moderate|weak|defeated|contested|unresolved",
   "formal_candidate":{{"suitable":false,"reason":"","premises":[],"conclusion":"","fidelity":"candidate_unvalidated"}}
 }}],
 "defeaters": [{{
   "id":"D1","target_type":"claim|argument|premise_use|ground",
   "target_id":"","attack_type":"rebutter|underminer|undercutter|exception|alternative_explanation",
   "ground_ids":[],"content":"","status":"supported|contested|unresolved"
 }}],
 "terminal_claim_ids_by_question": {{}},
 "completion_notes":[]
}}"""


def _critic_prompt(
    portfolio: dict[str, Any],
    graph: dict[str, Any],
    known_ground_ids: set[str],
) -> str:
    return f"""Act as an independent structural critic. Check this completed
argument graph for:
- any active question without terminal claims;
- any claim without an argument attempt;
- nonexistent claim or ground references;
- circularity;
- evidence presented as a claim or source presented as evidence;
- undercutters misrepresented as refutations;
- warrants that merely restate conclusions;
- argument assessments stronger than the recorded claim evidence;
- unsuitable or semantically unfaithful formalization candidates.

Definitions:
- A terminal claim is exactly a claim listed in terminal_claim_ids_by_question.
  Hinge and premise claims need not also be terminal.
- A direct ground-to-claim Argument is a valid argument attempt.
- Defeaters target existing argument/claim/ground IDs. Descriptive provenance
  fields are not graph references.
- Defeasible does not imply weak: a well-supported empirical argument may be
  strong while remaining non-deductive.
- Report only actual defects. Do not report successful checks as warnings.

ACTIVE QUESTIONS:
{json.dumps([q for q in portfolio["questions"] if q.get("disposition") == "active"], ensure_ascii=False)}
KNOWN GROUND IDS:
{json.dumps(sorted(known_ground_ids))}
GRAPH:
{json.dumps(graph, ensure_ascii=False)}

Return JSON:
{{"pass":true,"issues":[{{"severity":"error|warning","code":"","target_id":"","message":"","repair":""}}],"missing_argument_targets":[]}}"""


def formal_report(graph: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for argument in graph.get("arguments", []):
        candidate = argument.get("formal_candidate") or {}
        if not candidate.get("suitable"):
            rows.append(
                {
                    "argument_id": argument["id"],
                    "status": "not_formalized",
                    "reason": candidate.get("reason")
                    or "Argument is defeasible or lacks a suitable formalization.",
                }
            )
            continue
        try:
            result = cross_check_propositional(
                list(candidate.get("premises") or []),
                str(candidate.get("conclusion") or ""),
                formalization_fidelity=candidate.get(
                    "fidelity", "candidate_unvalidated"
                ),
            )
            rows.append(
                {
                    "argument_id": argument["id"],
                    "status": "checked",
                    "result": result,
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "argument_id": argument["id"],
                    "status": "formalization_error",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "principle": (
            "Solver results establish consequences of supplied formalizations; "
            "formalization fidelity remains a separate assessment."
        ),
        "backend": "Z3 plus independent exhaustive truth table for <=12 symbols",
        "arguments_scanned": len(rows),
        "formal_candidates_checked": sum(
            item["status"] == "checked" for item in rows
        ),
        "results": rows,
    }


def complete_run(
    *,
    run_dir: str | Path,
    api_key: str,
    budget_usd: float,
) -> dict[str, Any]:
    root = Path(run_dir)
    portfolio = _load(root / "question_portfolio.json")
    skeleton = _load(root / "argument_graph_skeleton.json")
    assessments = _load(root / "claim_assessments.json")
    grounds = normalize_grounds(root)
    known_ground_ids = {item["id"] for item in grounds}
    active_ids = {
        item["id"]
        for item in portfolio["questions"]
        if item.get("disposition") == "active"
    }

    ledger = BudgetLedger(root / "cost_ledger.jsonl", limit_usd=budget_usd)
    client = OpenRouterClient(api_key, ledger)
    first, first_reply = client.call_json(
        purpose="argument_completion",
        model=ARCHITECT,
        prompt=_architect_prompt(portfolio, skeleton, grounds, assessments),
        max_tokens=3800,
        temperature=0.05,
    )
    first["_provenance"] = {
        "model": first_reply.model,
        "response_id": first_reply.response_id,
    }
    _save(root / "argument_graph_completed.draft.json", first)

    critic, critic_reply = client.call_json(
        purpose="argument_completion_critic",
        model=CRITIC,
        prompt=_critic_prompt(portfolio, first, known_ground_ids),
        max_tokens=1800,
        temperature=0,
    )
    critic["_provenance"] = {
        "model": critic_reply.model,
        "response_id": critic_reply.response_id,
    }
    _save(root / "argument_graph_critic.json", critic)

    final = first
    if not critic.get("pass", False):
        revised, revised_reply = client.call_json(
            purpose="argument_completion_revision",
            model=ARCHITECT,
            prompt=_architect_prompt(
                portfolio, skeleton, grounds, assessments, critic=critic
            ),
            max_tokens=3800,
            temperature=0,
        )
        revised["_provenance"] = {
            "model": revised_reply.model,
            "response_id": revised_reply.response_id,
            "revision_of": first_reply.response_id,
        }
        final = revised

    issues = validate_graph_skeleton(
        final,
        active_question_ids=active_ids,
        known_ground_ids=known_ground_ids,
    )
    final["structural_validation"] = [item.to_dict() for item in issues]
    _save(root / "argument_graph_completed.json", final)
    formal = formal_report(final)
    _save(root / "formal_validation_report.json", formal)
    return {
        "graph": final,
        "critic": critic,
        "formal_report": formal,
        "budget": ledger.summary(),
    }


def _claim_completion_prompt(
    claim: dict[str, Any],
    grounds: list[dict[str, Any]],
    assessment: dict[str, Any],
) -> str:
    compact_assessment = {
        "verifier": assessment.get("verifier"),
        "falsifier": assessment.get("falsifier"),
        "comparator": assessment.get("comparator"),
        "derived_verdict": assessment.get("derived_verdict"),
    }
    return f"""Create the inferential activity for exactly one existing claim.
Do not add or rewrite claims and do not invent evidence.

The claim is a proposition vertex. Grounds are observations/statements that
arguments cite; they are not proposition vertices. Create exactly one
supporting Argument attempt, even if the attempt is weak or unresolved. Put
rebutting, undermining, or undercutting material in Defeater relations targeting
that Argument; do not create an "opposing argument" whose conclusion is still
the claim being challenged.

CLAIM:
{json.dumps(claim, ensure_ascii=False)}
AVAILABLE GROUNDS:
{json.dumps(grounds, ensure_ascii=False)}
EXISTING INDEPENDENT ASSESSMENT:
{json.dumps(compact_assessment, ensure_ascii=False)}

Return JSON:
{{
 "argument": {{
   "premise_claim_ids": [], "ground_ids": [],
   "inference_type": "", "scheme": "",
   "warrant_reconstruction": "",
   "warrant_fidelity": "faithful|plausible_reconstruction|confabulated|vacuous|unresolved",
   "strictness": "strict|defeasible", "assumptions": [], "exceptions": [],
   "critical_questions": [],
   "assessment": "strong|moderate|weak|defeated|contested|unresolved",
   "formal_candidate": {{
     "suitable": false, "reason": "", "premises": [],
     "conclusion": "", "fidelity": "candidate_unvalidated"
   }}
 }},
 "defeaters": [{{
   "attack_type": "rebutter|underminer|undercutter|exception|alternative_explanation",
   "ground_ids": [], "content": "",
   "status": "supported|contested|unresolved"
 }}]
}}"""


def _terminal_map_from_roles(claims: list[dict[str, Any]]) -> dict[str, list[str]]:
    terminal_map: dict[str, list[str]] = {}
    for claim in claims:
        for role in claim.get("roles") or []:
            words = str(role).split()
            if len(words) >= 2 and words[0].startswith("Q") and words[1] == "terminal":
                terminal_map.setdefault(words[0], []).append(claim["id"])
    return terminal_map


def _convert_challenge_arguments(
    arguments: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    support_by_claim = {
        item.get("conclusion_claim_id"): item.get("id")
        for item in arguments
        if item.get("inference_type") not in {"undermining", "rebutting", "undercutting"}
    }
    retained: list[dict[str, Any]] = []
    converted: list[dict[str, Any]] = []
    for item in arguments:
        if item.get("inference_type") not in {"undermining", "rebutting", "undercutting"}:
            retained.append(item)
            continue
        claim_id = str(item.get("conclusion_claim_id") or "")
        target_id = support_by_claim.get(claim_id)
        if not target_id:
            retained.append(item)
            continue
        converted.append(
            {
                "id": f"D-{claim_id}-converted",
                "target_type": "argument",
                "target_id": target_id,
                "attack_type": (
                    "undercutter"
                    if item.get("inference_type") in {"undermining", "undercutting"}
                    else "rebutter"
                ),
                "ground_ids": list(item.get("ground_ids") or []),
                "content": item.get("warrant_reconstruction", ""),
                "status": (
                    "supported"
                    if item.get("assessment") in {"strong", "moderate"}
                    else "contested"
                ),
                "source_argument_id": item.get("id"),
            }
        )
    return retained, converted


def repair_completed_run(
    *,
    run_dir: str | Path,
    api_key: str,
    budget_usd: float,
) -> dict[str, Any]:
    root = Path(run_dir)
    portfolio = _load(root / "question_portfolio.json")
    graph = _load(root / "argument_graph_completed.json")
    assessments = _load(root / "claim_assessments.json")
    grounds = (
        _load(root / "normalized_grounds.json")
        if (root / "normalized_grounds.json").exists()
        else normalize_grounds(root)
    )
    known_ground_ids = {item["id"] for item in grounds}
    active_ids = {
        item["id"]
        for item in portfolio["questions"]
        if item.get("disposition") == "active"
    }

    arguments, converted_defeaters = _convert_challenge_arguments(
        list(graph.get("arguments") or [])
    )
    graph["arguments"] = arguments
    graph["defeaters"] = list(graph.get("defeaters") or []) + converted_defeaters
    for defeater in graph["defeaters"]:
        defeater.pop("source_argument_id", None)
        if (
            defeater.get("id") == "D-C4-4"
            and defeater.get("attack_type") == "rebutter"
        ):
            defeater["attack_type"] = "undercutter"
    attempted = {
        str(item.get("conclusion_claim_id") or "") for item in graph["arguments"]
    }
    missing = [item for item in graph["claims"] if item["id"] not in attempted]

    ledger = BudgetLedger(root / "cost_ledger.jsonl", limit_usd=budget_usd)
    client = OpenRouterClient(api_key, ledger)
    completion_provenance: list[dict[str, str]] = []
    for claim in missing:
        claim_id = claim["id"]
        claim_grounds = [item for item in grounds if item["claim_id"] == claim_id]
        result, reply = client.call_json(
            purpose=f"focused_argument_completion:{claim_id}",
            model=ARCHITECT,
            prompt=_claim_completion_prompt(
                claim, claim_grounds, assessments.get(claim_id, {})
            ),
            max_tokens=2200,
            temperature=0,
        )
        argument = dict(result.get("argument") or {})
        argument["id"] = f"A-{claim_id}-support"
        argument["conclusion_claim_id"] = claim_id
        argument["premise_claim_ids"] = [
            item
            for item in argument.get("premise_claim_ids") or []
            if item in {candidate["id"] for candidate in graph["claims"]}
        ]
        argument["ground_ids"] = [
            item
            for item in argument.get("ground_ids") or []
            if item in known_ground_ids
        ]
        argument.setdefault(
            "formal_candidate",
            {
                "suitable": False,
                "reason": "No strict formalization was supplied.",
                "premises": [],
                "conclusion": "",
                "fidelity": "candidate_unvalidated",
            },
        )
        graph["arguments"].append(argument)
        for index, defeater in enumerate(result.get("defeaters") or [], start=1):
            item = dict(defeater)
            item["id"] = f"D-{claim_id}-{index}"
            item["target_type"] = "argument"
            item["target_id"] = argument["id"]
            item["ground_ids"] = [
                ground_id
                for ground_id in item.get("ground_ids") or []
                if ground_id in known_ground_ids
            ]
            graph["defeaters"].append(item)
        completion_provenance.append(
            {
                "claim_id": claim_id,
                "model": reply.model,
                "response_id": reply.response_id,
            }
        )

    graph["terminal_claim_ids_by_question"] = _terminal_map_from_roles(
        graph["claims"]
    )
    graph["completion_provenance"] = completion_provenance
    graph.setdefault("completion_notes", []).append(
        "Challenge-shaped pseudo-arguments were converted to Defeater relations."
    )
    issues = validate_graph_skeleton(
        graph,
        active_question_ids=active_ids,
        known_ground_ids=known_ground_ids,
    )
    graph["structural_validation"] = [item.to_dict() for item in issues]
    _save(root / "argument_graph_completed.json", graph)

    critic, critic_reply = client.call_json(
        purpose="repaired_graph_critic",
        model=CRITIC,
        prompt=_critic_prompt(portfolio, graph, known_ground_ids),
        max_tokens=2400,
        temperature=0,
    )
    critic["_provenance"] = {
        "model": critic_reply.model,
        "response_id": critic_reply.response_id,
    }
    _save(root / "argument_graph_repaired_critic.json", critic)
    formal = formal_report(graph)
    _save(root / "formal_validation_report.json", formal)
    return {
        "graph": graph,
        "critic": critic,
        "formal_report": formal,
        "budget": ledger.summary(),
    }
