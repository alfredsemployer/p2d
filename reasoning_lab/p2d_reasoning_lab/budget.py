"""Hard-budget accounting for paid model calls."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any


class BudgetExceeded(RuntimeError):
    """Raised before a call whose reservation would cross the run ceiling."""


@dataclass(frozen=True, slots=True)
class Reservation:
    purpose: str
    model: str
    amount: Decimal


class BudgetLedger:
    """Append-only cost ledger with conservative pre-call reservations.

    The pipeline is sequential, so a reservation need not coordinate concurrent
    callers. Actual cost comes from OpenRouter's non-streaming ``usage.cost``.
    """

    def __init__(self, path: str | Path, limit_usd: float | str = "3.00") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.limit = Decimal(str(limit_usd))
        if self.limit <= 0:
            raise ValueError("budget limit must be positive")
        self.spent = Decimal("0")
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                self.spent += Decimal(str(row["actual_cost_usd"]))

    @property
    def remaining(self) -> Decimal:
        return self.limit - self.spent

    def reserve(self, *, purpose: str, model: str, amount_usd: float) -> Reservation:
        amount = Decimal(str(amount_usd))
        if amount <= 0:
            raise ValueError("reservation must be positive")
        if self.spent + amount > self.limit:
            raise BudgetExceeded(
                f"{purpose}: reserving ${amount} would exceed "
                f"${self.limit} limit; ${self.remaining} remains"
            )
        return Reservation(purpose=purpose, model=model, amount=amount)

    def record(
        self,
        reservation: Reservation,
        *,
        actual_cost_usd: float,
        response_id: str,
        usage: dict[str, Any],
    ) -> None:
        actual = Decimal(str(actual_cost_usd))
        if actual < 0:
            raise ValueError("actual cost cannot be negative")
        # A provider could theoretically exceed our conservative reservation.
        # Record honestly and stop all subsequent calls if that occurs.
        self.spent += actual
        row = {
            "timestamp": datetime.now(UTC).isoformat(),
            "purpose": reservation.purpose,
            "model_requested": reservation.model,
            "reserved_usd": float(reservation.amount),
            "actual_cost_usd": float(actual),
            "response_id": response_id,
            "usage": usage,
            "cumulative_cost_usd": float(self.spent),
            "budget_limit_usd": float(self.limit),
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        if self.spent > self.limit:
            raise BudgetExceeded(
                f"provider-reported cost crossed the hard ceiling: ${self.spent}"
            )

    def summary(self) -> dict[str, float]:
        return {
            "limit_usd": float(self.limit),
            "spent_usd": float(self.spent),
            "remaining_usd": float(self.remaining),
        }
