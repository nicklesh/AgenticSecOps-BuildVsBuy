"""
Phishing Simulation & Awareness Agent
Generates varied lure templates for an authorized internal
security-awareness campaign, and flags repeat clickers for targeted
(never punitive) training. Requires HR/legal sign-off on the program
itself before use — see README.md. Depends on model_client.py from
Module 0 — copy it into this folder or adjust the import path.

Usage:
    python phishing_sim_agent.py
"""

import json
from collections import Counter

from model_client import ModelClient  # from Module 0
from pydantic import BaseModel


class LureTemplate(BaseModel):
    subject: str
    body: str
    theme: str  # e.g. "invoice", "mfa-fatigue", "hr-benefits"
    difficulty: str  # "easy" | "moderate" | "hard"


GENERATE_SYSTEM_PROMPT = """You are generating a simulated phishing
email for an authorized internal security-awareness campaign. This is
for training purposes only, run with organizational approval.

Generate a realistic but clearly template-varied lure using the theme
provided. Rotate structure and wording — never reuse a previous
template verbatim, since repeated exact wording defeats the purpose of
periodic testing.

Do not impersonate a specific named real individual. Use generic role
titles (e.g., "IT Support", "HR Benefits Team") rather than real
employee names.

Respond in JSON only: {subject, body, theme, difficulty}.
"""


def generate_lure(client: ModelClient, theme: str, difficulty: str) -> LureTemplate:
    response = client._call_raw(
        system=GENERATE_SYSTEM_PROMPT,
        user_content=json.dumps({"theme": theme, "difficulty": difficulty}),
    )
    parsed = json.loads(response)
    return LureTemplate(**parsed)


def flag_repeat_clickers(click_log_path: str, threshold: int = 2) -> list[str]:
    """Returns user IDs who've clicked more than `threshold` simulated
    campaigns — these get enrolled in targeted training, never
    disciplinary action, and never a public list."""
    clicks = Counter()
    try:
        with open(click_log_path) as f:
            for line in f:
                if not line.strip():
                    continue
                record = json.loads(line)
                clicks[record["user_id"]] += 1
    except FileNotFoundError:
        return []
    return [user for user, count in clicks.items() if count > threshold]


def main():
    client = ModelClient(provider="anthropic", model="claude-sonnet-5")

    lure = generate_lure(client, theme="invoice", difficulty="moderate")
    print(f"Generated lure: {lure.subject}")

    # Push `lure` into GoPhish via its API to launch the campaign —
    # left as an exercise per your GoPhish instance configuration.

    repeat_clickers = flag_repeat_clickers("./click_log.jsonl")
    if repeat_clickers:
        print(f"{len(repeat_clickers)} users flagged for targeted training")
        # Enroll in training here — never a punitive action, never a
        # public list. Route through HR's existing training system.


if __name__ == "__main__":
    main()
