"""
CSPM Triage Agent
Reads raw Prowler scan output, triages findings with an LLM, and writes
a structured triage_output.json for the (separate, explicit) PR-drafting
step in draft_pr.py.

Usage:
    prowler aws --output-formats json-asff --output-directory ./scans
    python agent.py
"""

import json
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

TRIAGE_PROMPT = """You are a cloud security triage assistant. You will be
given raw findings from a Prowler scan. For each finding:

1. Confirm the severity is justified given the resource type and exposure
   (Prowler's default severity is a starting point, not final).
2. Group findings that share a root cause (e.g., 12 buckets with the same
   missing encryption policy is one action item, not 12).
3. For each group, write:
   - A one-sentence plain-English explanation of the risk
   - Whether this is safe to auto-draft a fix for (see criteria below)
   - The specific remediation steps

Auto-draftable = true only if: the fix is a config change (not a resource
deletion), has no plausible legitimate reason to be intentional (e.g., a
public bucket that's clearly not meant to host a static site), and
affects non-production resources OR is a well-established best-practice
fix (e.g., enabling encryption at rest) with negligible risk of breaking
functionality.

Respond in JSON only: a list of objects with keys group_id, severity,
summary, auto_draftable, remediation_steps, affected_resources.
"""


def load_findings(path: str) -> list[dict]:
    with open(path) as f:
        data = json.load(f)
    # Adapt this line to whatever shape your Prowler output version uses.
    return data.get("findings", data)


def triage(findings: list[dict]) -> list[dict]:
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=4096,
        system=TRIAGE_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Findings:\n{json.dumps(findings, indent=2)}"
        }]
    )
    return json.loads(response.content[0].text)


def main():
    findings = load_findings("./scans/latest.json")
    triaged = triage(findings)

    auto_draftable = [f for f in triaged if f["auto_draftable"]]
    needs_review = [f for f in triaged if not f["auto_draftable"]]

    print(f"{len(auto_draftable)} findings eligible for draft PR")
    print(f"{len(needs_review)} findings need human review first")

    with open("./triage_output.json", "w") as f:
        json.dump(triaged, f, indent=2)


if __name__ == "__main__":
    main()
