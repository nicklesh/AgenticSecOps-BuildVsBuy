"""
GRC Evidence Agent
Pulls current control state, drafts a plain-English narrative via LLM,
and flags evidence that's gone stale. Depends on model_client.py from
Module 0 — copy it into this folder or adjust the import path.

Usage:
    python evidence_agent.py
"""

import json
import os
from datetime import datetime, timezone

from model_client import ModelClient, load_prompt  # from Module 0
from pydantic import BaseModel


class ControlEvidence(BaseModel):
    control_id: str
    status: str  # "met" | "not_met" | "needs_review"
    narrative: str
    checked_at: str = ""


TRIAGE_SYSTEM_PROMPT = """You are a compliance evidence assistant. You
will be given the raw current-state output for one control (e.g. "is
MFA enforced org-wide", "are access reviews happening quarterly").

Compare the raw state against the control's requirement and respond
with:
- status: "met", "not_met", or "needs_review" (use needs_review if the
  raw data is ambiguous — do not guess)
- narrative: a 2-3 sentence plain-English explanation an auditor could
  read alongside the raw evidence

Respond in JSON only, matching: {control_id, status, narrative}.
"""


def check_control(client: ModelClient, control_id: str, raw_state: dict) -> ControlEvidence:
    result = client.call_structured(
        system=TRIAGE_SYSTEM_PROMPT,
        user_content=json.dumps({"control_id": control_id, "raw_state": raw_state}),
        schema=ControlEvidence,
    )
    result.checked_at = datetime.now(timezone.utc).isoformat()
    return result


def freshness_check(evidence_store_path: str, max_age_days: int = 7) -> list[str]:
    """Returns control_ids whose evidence hasn't refreshed within
    max_age_days. Run this on a schedule — a silently broken collector
    is invisible until audit day otherwise."""
    stale = []
    if not os.path.exists(evidence_store_path):
        return stale
    with open(evidence_store_path) as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            checked_at = datetime.fromisoformat(record["checked_at"])
            age_days = (datetime.now(timezone.utc) - checked_at).days
            if age_days > max_age_days:
                stale.append(record["control_id"])
    return stale


def main():
    client = ModelClient(provider="google", model="gemini-3.1-pro")

    # Replace with real pulls from your cloud/IdP APIs — this is where
    # you adapt the module to your actual control set.
    controls_to_check = {
        "MFA-ORG-WIDE": {"mfa_enforced_pct": 100, "exceptions": []},
        "ACCESS-REVIEW-QUARTERLY": {"last_review_date": "2026-05-01"},
    }

    evidence = []
    for control_id, raw_state in controls_to_check.items():
        result = check_control(client, control_id, raw_state)
        evidence.append(result.model_dump())
        print(f"{control_id}: {result.status}")

    with open("./evidence_store.jsonl", "a") as f:
        for record in evidence:
            f.write(json.dumps(record) + "\n")

    stale = freshness_check("./evidence_store.jsonl")
    if stale:
        print(f"Stale evidence (>7 days) for: {stale}")


if __name__ == "__main__":
    main()
