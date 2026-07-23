"""Command-line entry points."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from .answer_revision import revise_and_audit_answer
from .evals import run_evaluations
from .closure import complete_run, repair_completed_run
from .formal import check_smt2, cross_check_propositional
from .openrouter import load_api_key
from .pipeline import run_pipeline
from .migration import migrate_legacy_run
from .reconstruct import build_reconstructed_graph
from .v03_evals import run_v03_evaluations


def _default_run_dir() -> Path:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return Path(__file__).resolve().parents[1] / "runs" / stamp


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="p2d-lab")
    sub = parser.add_subparsers(dest="command", required=True)

    pipeline = sub.add_parser("pipeline")
    pipeline.add_argument("--question", required=True)
    pipeline.add_argument("--budget", type=float, default=3.0)
    pipeline.add_argument("--key-file")
    pipeline.add_argument("--output-dir", type=Path, default=None)
    pipeline.add_argument("--as-of")

    evaluations = sub.add_parser("evals")
    evaluations.add_argument("--budget", type=float, default=3.0)
    evaluations.add_argument("--key-file")
    evaluations.add_argument("--run-dir", type=Path, required=True)
    evaluations.add_argument(
        "--eval-model", default="openai/gpt-5.6-luna"
    )
    evaluations.add_argument("--output-subdir", default="evals")
    evaluations.add_argument(
        "--eval-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "evals",
    )

    complete = sub.add_parser("complete")
    complete.add_argument("--budget", type=float, default=3.0)
    complete.add_argument("--key-file")
    complete.add_argument("--run-dir", type=Path, required=True)

    repair = sub.add_parser("repair-completion")
    repair.add_argument("--budget", type=float, default=3.0)
    repair.add_argument("--key-file")
    repair.add_argument("--run-dir", type=Path, required=True)

    revise_answer = sub.add_parser("revise-answer")
    revise_answer.add_argument("--budget", type=float, default=3.0)
    revise_answer.add_argument("--key-file")
    revise_answer.add_argument("--run-dir", type=Path, required=True)

    reconstruct = sub.add_parser("reconstruct")
    reconstruct.add_argument("--run-dir", type=Path, required=True)

    migrate = sub.add_parser("migrate-v03")
    migrate.add_argument("--run-dir", type=Path, required=True)
    migrate.add_argument("--valence-decisions", type=Path, required=True)

    evals_v03 = sub.add_parser("evals-v03")
    evals_v03.add_argument("--artifact", type=Path, required=True)
    evals_v03.add_argument("--output-dir", type=Path, required=True)

    overnight = sub.add_parser("overnight")
    overnight.add_argument("--question", required=True)
    overnight.add_argument("--budget", type=float, default=3.0)
    overnight.add_argument("--key-file")
    overnight.add_argument("--output-dir", type=Path, default=None)
    overnight.add_argument("--as-of")

    formal = sub.add_parser("formal")
    formal_sub = formal.add_subparsers(dest="formal_command", required=True)
    entail = formal_sub.add_parser("entail")
    entail.add_argument("--premise", action="append", default=[])
    entail.add_argument("--conclusion", required=True)
    entail.add_argument(
        "--fidelity",
        default="candidate_unvalidated",
        choices=[
            "exact_for_stated_scope",
            "partial",
            "approximate",
            "candidate_unvalidated",
            "unsuitable",
        ],
    )
    smt = formal_sub.add_parser("smt2")
    smt.add_argument("path", type=Path)
    smt.add_argument(
        "--fidelity",
        default="candidate_unvalidated",
        choices=[
            "exact_for_stated_scope",
            "partial",
            "approximate",
            "candidate_unvalidated",
            "unsuitable",
        ],
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "formal":
        if args.formal_command == "entail":
            result = cross_check_propositional(
                args.premise,
                args.conclusion,
                formalization_fidelity=args.fidelity,
            )
        else:
            result = check_smt2(
                args.path.read_text(encoding="utf-8"),
                formalization_fidelity=args.fidelity,
            ).to_dict()
        print(json.dumps(result, indent=2))
        return
    if args.command == "reconstruct":
        graph = build_reconstructed_graph(args.run_dir)
        print(
            json.dumps(
                {
                    "claims": len(graph["claims"]),
                    "arguments": len(graph["arguments"]),
                    "defeaters": len(graph["defeaters"]),
                    "structural_errors": sum(
                        item["severity"] == "error"
                        for item in graph["structural_validation"]
                    ),
                    "inferential_reachability": graph[
                        "inferential_reachability"
                    ],
                },
                indent=2,
            )
        )
        return
    if args.command == "migrate-v03":
        graph = migrate_legacy_run(
            args.run_dir,
            valence_decisions_path=args.valence_decisions,
        )
        print(
            json.dumps(
                {
                    "artifact_id": graph["artifact_id"],
                    "claims": len(graph["claims"]),
                    "arguments": len(graph["arguments"]),
                    "defeaters": len(graph["defeaters"]),
                    "formal_candidates_checked": graph["formal_validation"][
                        "formal_candidates_checked"
                    ],
                    "structural_errors": sum(
                        item["severity"] == "error"
                        for item in graph["structural_validation"]
                    ),
                },
                indent=2,
            )
        )
        return
    if args.command == "evals-v03":
        result = run_v03_evaluations(
            artifact_path=args.artifact,
            output_dir=args.output_dir,
        )
        print(json.dumps(result, indent=2))
        return

    key = load_api_key(args.key_file)
    if args.command == "complete":
        result = complete_run(
            run_dir=args.run_dir,
            api_key=key,
            budget_usd=args.budget,
        )
        print(
            json.dumps(
                {
                    "arguments": len(result["graph"].get("arguments", [])),
                    "defeaters": len(result["graph"].get("defeaters", [])),
                    "structural_errors": sum(
                        item["severity"] == "error"
                        for item in result["graph"].get(
                            "structural_validation", []
                        )
                    ),
                    "formal_candidates_checked": result["formal_report"][
                        "formal_candidates_checked"
                    ],
                    "budget": result["budget"],
                },
                indent=2,
            )
        )
        return
    if args.command == "repair-completion":
        result = repair_completed_run(
            run_dir=args.run_dir,
            api_key=key,
            budget_usd=args.budget,
        )
        print(
            json.dumps(
                {
                    "arguments": len(result["graph"].get("arguments", [])),
                    "defeaters": len(result["graph"].get("defeaters", [])),
                    "structural_errors": sum(
                        item["severity"] == "error"
                        for item in result["graph"].get(
                            "structural_validation", []
                        )
                    ),
                    "critic_pass": result["critic"].get("pass"),
                    "formal_candidates_checked": result["formal_report"][
                        "formal_candidates_checked"
                    ],
                    "budget": result["budget"],
                },
                indent=2,
            )
        )
        return
    if args.command == "revise-answer":
        result = revise_and_audit_answer(
            run_dir=args.run_dir,
            api_key=key,
            budget_usd=args.budget,
        )
        print(
            json.dumps(
                {
                    "audit_pass": result["audit"].get("pass"),
                    "audit_issues": len(result["audit"].get("issues", [])),
                    "budget": result["budget"],
                },
                indent=2,
            )
        )
        return
    if args.command == "evals":
        summary = run_evaluations(
            eval_dir=args.eval_dir,
            output_dir=args.run_dir / args.output_subdir,
            ledger_path=args.run_dir / "cost_ledger.jsonl",
            api_key=key,
            budget_usd=args.budget,
            eval_model=args.eval_model,
        )
        print(json.dumps(summary, indent=2))
        return

    output = args.output_dir or _default_run_dir()
    pipeline_error: str | None = None
    try:
        result = run_pipeline(
            output_dir=output,
            question=args.question,
            api_key=key,
            budget_usd=args.budget,
            as_of=args.as_of,
        )
        print(json.dumps(result["manifest"], indent=2))
    except Exception as exc:
        pipeline_error = f"{type(exc).__name__}: {exc}"
        (output / "pipeline_error.txt").write_text(
            pipeline_error + "\n", encoding="utf-8"
        )
        if args.command == "pipeline":
            raise

    if args.command == "overnight":
        summary = run_evaluations(
            eval_dir=Path(__file__).resolve().parents[1] / "evals",
            output_dir=output / "evals",
            ledger_path=output / "cost_ledger.jsonl",
            api_key=key,
            budget_usd=args.budget,
        )
        print(
            json.dumps(
                {
                    "output_dir": str(output),
                    "pipeline_error": pipeline_error,
                    "evaluation_summary": {
                        "completed_suites": summary["completed_suites"],
                        "mean_accuracy": summary["mean_accuracy"],
                        "budget": summary["budget"],
                    },
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
