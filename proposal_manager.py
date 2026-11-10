"""Safe governance proposal drafting utilities.

This module creates reviewable proposal documents only. It never signs, submits,
executes, or queues a governance transaction and it does not assert voting control.
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")


def validate_proposal(proposal: dict[str, Any]) -> None:
    required = {"id", "title", "summary", "discussion_url", "actions"}
    missing = required - proposal.keys()
    if missing:
        raise ValueError(f"missing proposal fields: {sorted(missing)}")
    if not SAFE_ID.fullmatch(str(proposal["id"])):
        raise ValueError("proposal id must be a lowercase safe identifier")
    if not str(proposal["discussion_url"]).startswith(("https://", "http://")):
        raise ValueError("discussion_url must be HTTP(S)")
    if not isinstance(proposal["actions"], list) or not proposal["actions"]:
        raise ValueError("actions must be a non-empty reviewable list")
    for action in proposal["actions"]:
        if not isinstance(action, dict) or not {"target", "description"} <= action.keys():
            raise ValueError("each action needs target and description")
        if "calldata" in action:
            raise ValueError("raw calldata is not accepted by the safe draft tool")


def create_draft(proposal: dict[str, Any], output_dir: str = "proposals") -> Path:
    validate_proposal(proposal)
    draft = {**proposal, "created_at": datetime.now(timezone.utc).isoformat(),
             "status": "draft-only", "execution": "disabled", "voting_power": "not_verified"}
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{proposal['id']}.json"
    path.write_text(json.dumps(draft, indent=2, ensure_ascii=False) + "\n")
    return path


def main() -> int:
    input_path = os.environ.get("PROPOSAL_INPUT", "proposal.example.json")
    output_dir = os.environ.get("PROPOSAL_OUTPUT_DIR", "proposals")
    try:
        proposal = json.loads(Path(input_path).read_text())
        path = create_draft(proposal, output_dir)
        print(f"Created review-only proposal draft: {path}")
        return 0
    except Exception as exc:
        print(f"Proposal draft failed closed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
