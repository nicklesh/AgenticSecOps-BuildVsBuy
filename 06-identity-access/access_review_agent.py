"""
Identity & Access Review Agent
Flags stale, excessive, or orphaned access based on IdP data. Never
executes a revocation — every recommendation is proposal-only, for
human review. Depends on model_client.py from Module 0 — copy it into
this folder or adjust the import path.

Usage:
    python access_review_agent.py
"""

import json
from datetime import datetime, timezone

from model_client import ModelClient  # from Module 0
from pydantic import BaseModel


class AccessFlag(BaseModel):
    user_id: str
    flag_type: str  # "stale" | "excessive" | "orphaned" | "ok"
    reasoning: str
    recommended_action: str


REVIEW_SYSTEM_PROMPT = """You are an access-review assistant. You'll be
given a list of user accounts with their role assignments, last-login
date, and department/team context.

For each account, flag:
- "stale": no login in 90+ days
- "excessive": role scope doesn't match the stated job function (e.g.,
  a support role with database admin access)
- "orphaned": account exists with no clear owner or matching
  department record (e.g., a former employee's account, an
  unattributed service account)
- "ok": access matches role, recent activity, no concerns

Never recommend revocation directly — recommended_action should always
be phrased as a proposal for human review (e.g., "recommend
recertification with manager", "recommend downgrade to read-only,
confirm with IT"), never an instruction to execute.

Respond in JSON only: a list of {user_id, flag_type, reasoning,
recommended_action}.
"""


def review_accounts(client: ModelClient, accounts: list[dict]) -> list[AccessFlag]:
    response = client._call_raw(
        system=REVIEW_SYSTEM_PROMPT,
        user_content=json.dumps({"accounts": accounts}),
    )
    parsed = json.loads(response)
    return [AccessFlag(**item) for item in parsed]


def main():
    client = ModelClient(provider="anthropic", model="claude-sonnet-5")

    # Replace with a real pull from your IdP's admin API.
    accounts = [
        {"user_id": "u_1234", "role": "support-agent", "scope": ["db:admin"],
         "last_login": "2026-03-01", "department": "Customer Support"},
        {"user_id": "u_5678", "role": "engineer", "scope": ["repo:write"],
         "last_login": "2026-08-01", "department": "Engineering"},
    ]

    flags = review_accounts(client, accounts)
    needs_attention = [f for f in flags if f.flag_type != "ok"]
    print(f"{len(needs_attention)} accounts flagged for review out of {len(accounts)}")

    with open("./access_review_report.jsonl", "a") as f:
        for flag in flags:
            record = flag.model_dump()
            record["reviewed_at"] = datetime.now(timezone.utc).isoformat()
            f.write(json.dumps(record) + "\n")

    for f in needs_attention:
        print(f"  - {f.user_id} ({f.flag_type}): {f.recommended_action}")


if __name__ == "__main__":
    main()
