"""Z3-backed formal checks with an independent truth-table cross-check.

These functions prove consequences of supplied formalizations. They deliberately
carry formalization fidelity as metadata; they do not infer that fidelity from a
successful solver result.
"""

from __future__ import annotations

import ast
import itertools
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

import z3


FormalStatus = Literal[
    "proved",
    "disproved",
    "satisfiable",
    "unsatisfiable",
    "inconsistent_premises",
    "unknown",
]
Fidelity = Literal[
    "exact_for_stated_scope",
    "partial",
    "approximate",
    "candidate_unvalidated",
    "unsuitable",
]


class FormalExpressionError(ValueError):
    pass


@dataclass(slots=True)
class FormalResult:
    status: FormalStatus
    backend: str
    backend_version: str
    formalization_fidelity: Fidelity
    symbols: list[str] = field(default_factory=list)
    countermodel: dict[str, Any] | None = None
    model: dict[str, Any] | None = None
    unsat_core: list[str] = field(default_factory=list)
    assertions_checked: int = 0
    message: str = ""
    artifact: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class _PropositionalParser:
    _function_arity = {"implies": 2, "iff": 2, "xor": 2}

    def __init__(self) -> None:
        self.variables: dict[str, z3.BoolRef] = {}

    def parse(self, expression: str) -> z3.BoolRef:
        try:
            tree = ast.parse(expression, mode="eval")
        except SyntaxError as exc:
            raise FormalExpressionError(str(exc)) from exc
        return self._convert(tree.body)

    def _convert(self, node: ast.AST) -> z3.BoolRef:
        if isinstance(node, ast.Name):
            if node.id in self._function_arity:
                raise FormalExpressionError("logical function used without a call")
            self.variables.setdefault(node.id, z3.Bool(node.id))
            return self.variables[node.id]
        if isinstance(node, ast.Constant) and isinstance(node.value, bool):
            return z3.BoolVal(node.value)
        if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
            return z3.And(*(self._convert(value) for value in node.values))
        if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
            return z3.Or(*(self._convert(value) for value in node.values))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return z3.Not(self._convert(node.operand))
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in self._function_arity
            and not node.keywords
        ):
            name = node.func.id
            expected = self._function_arity[name]
            if len(node.args) != expected:
                raise FormalExpressionError(f"{name} expects {expected} arguments")
            left, right = (self._convert(argument) for argument in node.args)
            if name == "implies":
                return z3.Implies(left, right)
            if name == "iff":
                return left == right
            return z3.Xor(left, right)
        raise FormalExpressionError(
            f"unsupported propositional syntax: {ast.dump(node)}"
        )


def _model_dict(
    model: z3.ModelRef, variables: dict[str, z3.BoolRef]
) -> dict[str, bool]:
    return {
        name: z3.is_true(model.eval(symbol, model_completion=True))
        for name, symbol in sorted(variables.items())
    }


def check_propositional_entailment(
    premises: list[str],
    conclusion: str,
    *,
    formalization_fidelity: Fidelity = "candidate_unvalidated",
) -> FormalResult:
    """Check whether ``premises |= conclusion`` using Z3.

    Premise consistency is tested first so an inconsistent set is never
    reported as a useful proof by explosion.
    """

    parser = _PropositionalParser()
    premise_terms = [parser.parse(item) for item in premises]
    conclusion_term = parser.parse(conclusion)

    premise_solver = z3.Solver()
    tracked_names: list[str] = []
    for index, term in enumerate(premise_terms):
        label = z3.Bool(f"premise_{index}")
        tracked_names.append(str(label))
        premise_solver.assert_and_track(term, label)
    premise_status = premise_solver.check()
    symbols = sorted(parser.variables)
    version = z3.get_version_string()

    if premise_status == z3.unsat:
        return FormalResult(
            status="inconsistent_premises",
            backend="z3",
            backend_version=version,
            formalization_fidelity=formalization_fidelity,
            symbols=symbols,
            unsat_core=[str(item) for item in premise_solver.unsat_core()],
            assertions_checked=len(premises),
            message=(
                "The premises are inconsistent; vacuous entailment is not "
                "accepted as a usable proof."
            ),
        )
    if premise_status == z3.unknown:
        return FormalResult(
            status="unknown",
            backend="z3",
            backend_version=version,
            formalization_fidelity=formalization_fidelity,
            symbols=symbols,
            assertions_checked=len(premises),
            message=f"Z3 could not resolve premise consistency: {premise_solver.reason_unknown()}",
        )

    entailment_solver = z3.Solver()
    entailment_solver.add(*premise_terms)
    entailment_solver.add(z3.Not(conclusion_term))
    status = entailment_solver.check()
    if status == z3.unsat:
        return FormalResult(
            status="proved",
            backend="z3",
            backend_version=version,
            formalization_fidelity=formalization_fidelity,
            symbols=symbols,
            assertions_checked=len(premises) + 1,
            message="No model satisfies every premise while falsifying the conclusion.",
            artifact={
                "premises_smt2": [term.sexpr() for term in premise_terms],
                "negated_conclusion_smt2": z3.Not(conclusion_term).sexpr(),
            },
        )
    if status == z3.sat:
        return FormalResult(
            status="disproved",
            backend="z3",
            backend_version=version,
            formalization_fidelity=formalization_fidelity,
            symbols=symbols,
            countermodel=_model_dict(entailment_solver.model(), parser.variables),
            assertions_checked=len(premises) + 1,
            message="A countermodel satisfies every premise and falsifies the conclusion.",
        )
    return FormalResult(
        status="unknown",
        backend="z3",
        backend_version=version,
        formalization_fidelity=formalization_fidelity,
        symbols=symbols,
        assertions_checked=len(premises) + 1,
        message=f"Z3 returned unknown: {entailment_solver.reason_unknown()}",
    )


def check_smt2(
    assertions: str,
    *,
    formalization_fidelity: Fidelity = "candidate_unvalidated",
    timeout_ms: int = 10_000,
) -> FormalResult:
    """Check satisfiability of SMT-LIB2 assertions.

    ``assertions`` may contain declarations and assertions but must not contain
    commands such as ``check-sat``. Z3's parser rejects unsupported commands.
    """

    try:
        parsed = z3.parse_smt2_string(assertions)
    except z3.Z3Exception as exc:
        raise FormalExpressionError(str(exc)) from exc
    solver = z3.Solver()
    solver.set(timeout=timeout_ms)
    solver.add(parsed)
    status = solver.check()
    common = {
        "backend": "z3-smt2",
        "backend_version": z3.get_version_string(),
        "formalization_fidelity": formalization_fidelity,
        "assertions_checked": len(parsed),
        "artifact": {"smt2": assertions},
    }
    if status == z3.sat:
        model = solver.model()
        values = {
            declaration.name(): str(model[declaration])
            for declaration in model.decls()
        }
        return FormalResult(
            status="satisfiable",
            model=values,
            message="The SMT assertions are satisfiable.",
            **common,
        )
    if status == z3.unsat:
        return FormalResult(
            status="unsatisfiable",
            message="The SMT assertions are unsatisfiable.",
            **common,
        )
    return FormalResult(
        status="unknown",
        message=f"Z3 returned unknown: {solver.reason_unknown()}",
        **common,
    )


def truth_table_entailment(
    premises: list[str], conclusion: str, *, maximum_symbols: int = 12
) -> tuple[bool | None, dict[str, bool] | None]:
    """Independent exhaustive cross-check for small propositional problems."""

    parser = _PropositionalParser()
    premise_terms = [parser.parse(item) for item in premises]
    conclusion_term = parser.parse(conclusion)
    names = sorted(parser.variables)
    if len(names) > maximum_symbols:
        return None, None

    def evaluate(term: z3.BoolRef, assignment: dict[str, bool]) -> bool:
        substitutions = [
            (parser.variables[name], z3.BoolVal(value))
            for name, value in assignment.items()
        ]
        return z3.is_true(z3.simplify(z3.substitute(term, *substitutions)))

    found_satisfying_premises = False
    for values in itertools.product((False, True), repeat=len(names)):
        assignment = dict(zip(names, values, strict=True))
        if not all(evaluate(term, assignment) for term in premise_terms):
            continue
        found_satisfying_premises = True
        if not evaluate(conclusion_term, assignment):
            return False, assignment
    if not found_satisfying_premises:
        return None, None
    return True, None


def cross_check_propositional(
    premises: list[str],
    conclusion: str,
    *,
    formalization_fidelity: Fidelity = "candidate_unvalidated",
) -> dict[str, Any]:
    z3_result = check_propositional_entailment(
        premises,
        conclusion,
        formalization_fidelity=formalization_fidelity,
    )
    table_result, table_countermodel = truth_table_entailment(premises, conclusion)
    expected = {
        "proved": True,
        "disproved": False,
        "inconsistent_premises": None,
        "unknown": None,
    }[z3_result.status]
    return {
        "z3": z3_result.to_dict(),
        "truth_table": {
            "entailed": table_result,
            "countermodel": table_countermodel,
        },
        "agreement": expected == table_result,
    }
