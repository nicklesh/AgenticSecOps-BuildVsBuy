"""
SOC Alert-Triage Agent
Investigates alerts, drafts a verdict with reasoning, and flags only
high-confidence false positives as auto-close eligible. A weekly
sampling audit of auto-closed alerts is required, not optional — see
README.md. Depends on model_client.py from Module 0 — copy it into
this folder or adjust the import path.

Usage:
    python triage_agent.py
"""

import json
import random
from datetime import datetime, timezone

from model_client import ModelClient  # from Module 0
from pydantic import BaseModel


class TriageVerdict(BaseModel):
    alert_id: str
    verdict: str  # "true_positive" | "false_positive" | "needs_escalation"
    confidence: str  # "high" | "medium" | "low"
    reasoning: str


TRIAGE_SYSTEM_PROMPT = """You are a SOC alert-triage assistant. You'll
be given a raw alert (source, signature, affected asset) plus context:
asset criticality, recent related alerts, and any threat-intel matches
for observed indicators.

Draft a verdict:
- "true_positive": genuine malicious activity, needs response
- "false_positive": benign activity that matched a detection rule
- "needs_escalation": you don't have enough signal to decide
  confidently — use this rather than guessing on ambiguous cases

Set confidence honestly. A "low confidence false_positive" should
never be auto-closed — that combination should always route to
needs_escalation instead, since a confident wrong answer is worse than
an honest "I'm not sure."

Respond in JSON only: {alert_id, verdict, confidence, reasoning}.
"""


def triage_alert(client: ModelClient, alert: dict, context: dict) -> TriageVerdict:
    response = client._call_raw(
        system=TRIAGE_SYSTEM_PROMPT,
        user_content=json.dumps({"alert": alert, "context": context}),
    )
    parsed = json.loads(response)
    return TriageVerdict(**parsed)


def should_auto_close(verdict: TriageVerdict) -> bool:
    """Only high-confidence false positives are eligible for auto-close
    — and even then, see the sampling-audit requirement below.
    Everything else routes to a human queue."""
    return verdict.verdict == "false_positive" and verdict.confidence == "high"


def weekly_sampling_audit(verdict_log_path: str, sample_rate: float = 0.2) -> list[dict]:
    """Returns a random sample of auto-closed verdicts for human review.
    Run this every week without exception — it's how you catch verdict
    drift before it becomes a missed breach, not after."""
    auto_closed = []
    try:
        with open(verdict_log_path) as f:
            for line in f:
                if not line.strip():
                    continue
                record = json.loads(line)
                if record.get("auto_closed"):
                    auto_closed.append(record)
    except FileNotFoundError:
        return []
    sample_size = max(1, int(len(auto_closed) * sample_rate))
    return random.sample(auto_closed, min(sample_size, len(auto_closed)))


def main():
    client = ModelClient(provider="anthropic", model="claude-sonnet-5")

    # Replace with a real pull from your SIEM/EDR's alert API.
    alert = {"alert_id": "a_9001", "source": "EDR", "signature": "suspicious_process_spawn"}
    context = {"asset_criticality": "high", "threat_intel_matches": []}

    verdict = triage_alert(client, alert, context)
    auto_close = should_auto_close(verdict)

    print(f"{verdict.alert_id}: {verdict.verdict} ({verdict.confidence}) — auto_close={auto_close}")

    with open("./verdict_log.jsonl", "a") as f:
        record = verdict.model_dump()
        record["auto_closed"] = auto_close
        record["triaged_at"] = datetime.now(timezone.utc).isoformat()
        f.write(json.dumps(record) + "\n")


if __name__ == "__main__":
    main()
