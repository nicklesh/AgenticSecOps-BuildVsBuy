"""
SAST/DAST + OWASP Top 10 Triage Agent
Runs Semgrep static analysis, classifies findings against OWASP Top 10
categories, and flags which are safe to auto-draft a fix for. Depends
on model_client.py from Module 0 — copy it into this folder or adjust
the import path.

Usage:
    python sast_dast_agent.py
"""

import json
import subprocess
from datetime import datetime, timezone

from model_client import ModelClient  # from Module 0
from pydantic import BaseModel


class TriagedFinding(BaseModel):
    finding_id: str
    owasp_category: str  # e.g. "A03:2021 - Injection"
    severity: str  # "critical" | "high" | "medium" | "low"
    auto_fixable: bool
    reasoning: str


TRIAGE_SYSTEM_PROMPT = """You are an application security triage
assistant. You'll be given raw findings from a Semgrep static-analysis
scan (and optionally OWASP ZAP dynamic-scan results).

For each finding:
1. Classify it against the relevant OWASP Top 10 (2021) category.
2. Assign severity based on actual exploitability in this codebase's
   context, not just the scanner's default rating.
3. Set auto_fixable = true only if the fix is mechanical and
   low-risk (e.g., adding a missing input-sanitization call using an
   established library function already used elsewhere in the
   codebase) — never for anything touching authentication or
   authorization logic.

Respond in JSON only: a list of {finding_id, owasp_category, severity,
auto_fixable, reasoning}.
"""


def run_semgrep(target_dir: str) -> list[dict]:
    result = subprocess.run(
        ["semgrep", "--config=auto", "--json", target_dir],
        capture_output=True, text=True, timeout=600,
    )
    parsed = json.loads(result.stdout)
    return parsed.get("results", [])


def triage(client: ModelClient, findings: list[dict]) -> list[TriagedFinding]:
    response = client._call_raw(
        system=TRIAGE_SYSTEM_PROMPT,
        user_content=json.dumps({"findings": findings}),
    )
    parsed = json.loads(response)
    return [TriagedFinding(**item) for item in parsed]


def main(target_dir: str):
    client = ModelClient(provider="anthropic", model="claude-sonnet-5")

    findings = run_semgrep(target_dir)
    print(f"{len(findings)} raw findings from Semgrep")

    if not findings:
        return

    triaged = triage(client, findings)
    auto_fixable = [t for t in triaged if t.auto_fixable]
    print(f"{len(auto_fixable)} findings eligible for a draft fix PR")
    print(f"{len(triaged) - len(auto_fixable)} findings need human review")

    with open("./triage_output.jsonl", "a") as f:
        for t in triaged:
            record = t.model_dump()
            record["scanned_at"] = datetime.now(timezone.utc).isoformat()
            f.write(json.dumps(record) + "\n")

    # PR-opening step deliberately left separate — see the CSPM module's
    # draft_pr.py for the same pattern applied to this module.


if __name__ == "__main__":
    main(target_dir=".")
