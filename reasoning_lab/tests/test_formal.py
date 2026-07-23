import pytest

from p2d_reasoning_lab.formal import (
    FormalExpressionError,
    check_propositional_entailment,
    check_smt2,
    cross_check_propositional,
)


def test_modus_ponens_is_proved():
    result = check_propositional_entailment(["implies(P, Q)", "P"], "Q")
    assert result.status == "proved"


def test_affirming_consequent_has_countermodel():
    result = check_propositional_entailment(["implies(P, Q)", "Q"], "P")
    assert result.status == "disproved"
    assert result.countermodel == {"P": False, "Q": True}


def test_inconsistent_premises_are_not_usable_proof():
    result = check_propositional_entailment(["P", "not P"], "Q")
    assert result.status == "inconsistent_premises"
    assert result.unsat_core


def test_truth_table_agrees_with_z3():
    result = cross_check_propositional(
        ["implies(P, Q)", "implies(Q, R)"], "implies(P, R)"
    )
    assert result["agreement"] is True
    assert result["z3"]["status"] == "proved"


def test_fidelity_is_not_upgraded_by_solver():
    result = check_propositional_entailment(
        ["P"], "P", formalization_fidelity="candidate_unvalidated"
    )
    assert result.status == "proved"
    assert result.formalization_fidelity == "candidate_unvalidated"


def test_rejects_arbitrary_python_syntax():
    with pytest.raises(FormalExpressionError):
        check_propositional_entailment(["__import__('os')"], "P")


def test_smt_linear_arithmetic_satisfiable():
    result = check_smt2(
        """
        (declare-const x Int)
        (assert (> x 3))
        (assert (< x 5))
        """
    )
    assert result.status == "satisfiable"
    assert result.model["x"] == "4"


def test_smt_linear_arithmetic_unsatisfiable():
    result = check_smt2(
        """
        (declare-const x Real)
        (assert (> x 3))
        (assert (< x 2))
        """
    )
    assert result.status == "unsatisfiable"
