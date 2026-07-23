import json

import pytest

from p2d_reasoning_lab.budget import BudgetExceeded, BudgetLedger


def test_budget_records_actual_cost(tmp_path):
    ledger = BudgetLedger(tmp_path / "ledger.jsonl", limit_usd=1)
    reservation = ledger.reserve(purpose="x", model="m", amount_usd=0.5)
    ledger.record(
        reservation,
        actual_cost_usd=0.1,
        response_id="r",
        usage={"prompt_tokens": 1},
    )
    assert ledger.summary() == {
        "limit_usd": 1.0,
        "spent_usd": 0.1,
        "remaining_usd": 0.9,
    }
    row = json.loads((tmp_path / "ledger.jsonl").read_text())
    assert row["response_id"] == "r"


def test_budget_reloads_append_only_ledger(tmp_path):
    path = tmp_path / "ledger.jsonl"
    first = BudgetLedger(path, limit_usd=1)
    reservation = first.reserve(purpose="x", model="m", amount_usd=0.2)
    first.record(reservation, actual_cost_usd=0.12, response_id="r", usage={})
    second = BudgetLedger(path, limit_usd=1)
    assert second.spent == first.spent


def test_budget_rejects_over_reservation(tmp_path):
    ledger = BudgetLedger(tmp_path / "ledger.jsonl", limit_usd=0.2)
    with pytest.raises(BudgetExceeded):
        ledger.reserve(purpose="x", model="m", amount_usd=0.21)
