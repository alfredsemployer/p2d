"""Revise and independently audit an AnswerBundle without redoing research."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .budget import BudgetLedger
from .openrouter import OpenRouterClient


WRITER = "openai/gpt-5.6-luna"
AUDITOR = "google/gemini-2.5-pro"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _compact_assessments(assessments: dict[str, Any]) -> dict[str, Any]:
    return {
        claim_id: {
            "claim": record.get("claim"),
            "verifier": {
                "exact_proposition_established": record.get("verifier", {}).get(
                    "exact_proposition_established"
                ),
                "holds": record.get("verifier", {}).get("holds"),
                "rationale": record.get("verifier", {}).get("rationale"),
            },
            "comparator": record.get("comparator"),
            "derived_verdict": record.get("derived_verdict"),
        }
        for claim_id, record in assessments.items()
    }


def revise_and_audit_answer(
    *,
    run_dir: str | Path,
    api_key: str,
    budget_usd: float,
) -> dict[str, Any]:
    root = Path(run_dir)
    original = _load(root / "answer_bundle.json")
    assessments = _compact_assessments(_load(root / "claim_assessments.json"))
    prior_audit = _load(root / "answer_audit.json")
    ledger = BudgetLedger(root / "cost_ledger.jsonl", limit_usd=budget_usd)
    client = OpenRouterClient(api_key, ledger)

    revision_prompt = f"""Revise this AnswerBundle for strict claim fidelity.
Preserve its JSON schema and useful detail. Do not add factual claims or
re-decide the recorded verdicts.

Rules:
- Limited coverage must remain explicit and verdicts provisional.
- A safe weakening such as "appears competitive" is permitted.
- "Insufficient" means not established by current evidence, not false.
- A failed support route does not refute its conclusion.
- Do not synthesize two supported claims into a new significance claim unless
  that synthesis itself is an assessed claim.
- Preserve conditions, comparison classes, time bounds, and hosted-versus-
  checkpoint distinctions.
- Treat the prior audit as fallible. Fix genuine unsupported synthesis but do
  not strengthen language merely because the prior auditor objected to safe
  weakening.

ASSESSMENTS:
{json.dumps(assessments, ensure_ascii=False)}
ORIGINAL ANSWER:
{json.dumps(original, ensure_ascii=False)}
PRIOR AUDIT:
{json.dumps(prior_audit, ensure_ascii=False)}

Return the complete revised AnswerBundle JSON only."""
    revised, revision_reply = client.call_json(
        purpose="answer_bundle_revision",
        model=WRITER,
        prompt=revision_prompt,
        max_tokens=2400,
        temperature=0,
    )
    revised["_provenance"] = {
        "model": revision_reply.model,
        "response_id": revision_reply.response_id,
        "revision_of": original.get("_provenance", {}).get("response_id"),
    }
    _save(root / "answer_bundle_revised.json", revised)

    audit_prompt = f"""Independently audit every world-facing assertion in this
AnswerBundle against the supplied claim assessments.

Classify only real fidelity defects:
- unsupported_strengthening
- unsupported_synthesis
- scope_drift
- modality_drift
- precision_drift
- failure_to_false

Important calibration:
- Safe weakening is entailed, not modality drift.
- "Not established by current evidence" faithfully represents insufficient
  evidence; "false" does not.
- Restating a precise claim less specifically is allowed if its meaning and
  scope are preserved.
- An overall synthesis needs its own inferential support; juxtaposed claims do
  not automatically entail a new "significance" or "frontier" claim.
- Limited coverage blocks an unqualified terminal answer but does not erase
  the recorded evidential state.

ASSESSMENTS:
{json.dumps(assessments, ensure_ascii=False)}
ANSWER:
{json.dumps(revised, ensure_ascii=False)}

Return JSON:
{{"pass":true,"issues":[{{"text":"","type":"","why":"","claim_ids":[]}}],
"calibration_notes":[]}}"""
    audit, audit_reply = client.call_json(
        purpose="independent_answer_audit",
        model=AUDITOR,
        prompt=audit_prompt,
        max_tokens=1800,
        temperature=0,
    )
    audit["_provenance"] = {
        "model": audit_reply.model,
        "response_id": audit_reply.response_id,
    }
    _save(root / "answer_audit_independent.json", audit)
    return {
        "answer": revised,
        "audit": audit,
        "budget": ledger.summary(),
    }
