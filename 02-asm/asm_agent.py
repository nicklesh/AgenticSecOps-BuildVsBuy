"""
ASM Diff & Triage Agent
Compares today's recon scan against the last known inventory and
classifies what's new. Depends on model_client.py from Module 0 — copy
it into this folder or adjust the import path.

Usage:
    subfinder -d yourcompany.com -o ./scans/subdomains.txt
    amass enum -passive -d yourcompany.com -o ./scans/amass_output.txt
    python asm_agent.py
"""

import json
import os
from datetime import datetime, timezone

from model_client import ModelClient  # from Module 0
from pydantic import BaseModel


class AssetClassification(BaseModel):
    asset: str
    classification: str  # "known" | "new_needs_review" | "anomaly"
    reasoning: str


DIFF_SYSTEM_PROMPT = """You are an attack-surface triage assistant.
You'll be given a list of newly discovered assets (subdomains, exposed
services) that weren't in the previous scan. For each, classify it:

- "known": clearly part of expected infrastructure (e.g. a standard
  naming pattern matching known services)
- "new_needs_review": plausible but not obviously expected — needs a
  human to confirm it's intentional
- "anomaly": unusual enough to flag with higher urgency (e.g. an
  exposed admin panel, a service on an unexpected port, a naming
  pattern suggesting a forgotten dev/test environment)

Respond in JSON only, one object per asset: {asset, classification,
reasoning}.
"""


def load_current_scan(subfinder_path: str, amass_path: str) -> set[str]:
    assets = set()
    for path in [subfinder_path, amass_path]:
        if os.path.exists(path):
            with open(path) as f:
                assets.update(line.strip() for line in f if line.strip())
    return assets


def load_previous_inventory(path: str) -> set[str]:
    if not os.path.exists(path):
        return set()
    with open(path) as f:
        return set(json.load(f).get("assets", []))


def diff_and_triage(client: ModelClient, new_assets: list) -> list:
    if not new_assets:
        return []
    # Adapt this call to however your ModelClient handles list-typed
    # schemas — Module 0's example wraps a single pydantic model, so
    # for a list response either loop per-asset or extend call_structured
    # to accept a wrapper model like `class Batch(BaseModel): items: list[AssetClassification]`.
    result = client.call_structured(
        system=DIFF_SYSTEM_PROMPT,
        user_content=json.dumps({"new_assets": new_assets}),
        schema=AssetClassification,
    )
    return [result]


def main():
    client = ModelClient(provider="anthropic", model="claude-sonnet-5")

    current = load_current_scan("./scans/subdomains.txt", "./scans/amass_output.txt")
    previous = load_previous_inventory("./inventory.json")

    new_assets = current - previous
    removed_assets = previous - current

    print(f"{len(new_assets)} new assets, {len(removed_assets)} removed assets")

    triaged = diff_and_triage(client, list(new_assets))
    anomalies = [t for t in triaged if t.classification == "anomaly"]

    if anomalies:
        print(f"{len(anomalies)} anomalies flagged for immediate review")
        for a in anomalies:
            print(f"  - {a.asset}: {a.reasoning}")

    with open("./inventory.json", "w") as f:
        json.dump({
            "assets": list(current),
            "last_scan": datetime.now(timezone.utc).isoformat(),
        }, f, indent=2)


if __name__ == "__main__":
    main()
