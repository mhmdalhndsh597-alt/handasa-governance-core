"""Read-only weighted-vote auditor for supplied or indexed vote records."""
from __future__ import annotations

import json
import os
from decimal import Decimal
from pathlib import Path
from typing import Any


def summarize_votes(votes: list[dict[str, Any]], quorum: Decimal) -> dict[str, Any]:
    for vote in votes:
        if Decimal(str(vote.get("weight", 0))) < 0:
            raise ValueError("vote weight cannot be negative")
    for_total = sum((Decimal(str(v.get("weight", 0))) for v in votes if v.get("support") is True), Decimal("0"))
    against_total = sum((Decimal(str(v.get("weight", 0))) for v in votes if v.get("support") is False), Decimal("0"))
    abstain_total = sum((Decimal(str(v.get("weight", 0))) for v in votes if v.get("support") is None), Decimal("0"))
    total = for_total + against_total + abstain_total
    support_pct = (for_total / total * Decimal("100")) if total else Decimal("0")
    quorum_pct = (total / quorum * Decimal("100")) if quorum > 0 else Decimal("0")
    return {"for_weight": str(for_total), "against_weight": str(against_total), "abstain_weight": str(abstain_total),
            "total_weight": str(total), "support_percent": str(support_pct.quantize(Decimal("0.01"))),
            "quorum_percent": str(quorum_pct.quantize(Decimal("0.01"))), "quorum_reached": total >= quorum,
            "voters": len(votes), "weight_basis": "supplied_locked-or-delegated-weight; not independently verified"}


def main() -> int:
    try:
        votes = json.loads(Path(os.environ.get("VOTES_FILE", "votes.example.json")).read_text())
        quorum = Decimal(os.environ.get("QUORUM_WEIGHT", "0"))
        print(json.dumps(summarize_votes(votes, quorum), indent=2))
        return 0
    except Exception as exc:
        print(f"Vote audit failed closed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
