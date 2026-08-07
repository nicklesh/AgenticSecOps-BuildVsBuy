"""
Vulnerability Prioritization & Patch Agent
Scans a target, cross-references findings against CISA's Known
Exploited Vulnerabilities catalog, and ranks by priority. Depends on
model_client.py from Module 0 — copy it into this folder or adjust the
import path.

Usage:
    python patch_agent.py
"""

import json
import subprocess
import urllib.request
from datetime import datetime, timezone

from model_client import ModelClient  # from Module 0
from pydantic import BaseModel

KEV_FEED_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"


class PatchPriority(BaseModel):
    cve_id: str
    priority: str  # "patch_now" | "patch_this_sprint" | "monitor"
    reasoning: str
    known_exploited: bool


PRIORITIZE_SYSTEM_PROMPT = """You are a vulnerability prioritization
assistant. You'll be given scan findings (CVE IDs, affected packages,
CVSS scores) plus a list of which CVEs are in CISA's Known Exploited
Vulnerabilities catalog, and asset criticality context.

For each finding, assign priority:
- "patch_now": known-exploited AND on a critical/internet-facing asset
- "patch_this_sprint": known-exploited but lower-criticality asset, OR
  high CVSS on a critical asset without confirmed exploitation
- "monitor": neither known-exploited nor on a critical path — track it,
  don't drop everything for it

Respond in JSON only: a list of {cve_id, priority, reasoning,
known_exploited}.
"""


def fetch_kev_catalog() -> set[str]:
    with urllib.request.urlopen(KEV_FEED_URL, timeout=30) as response:
        data = json.loads(response.read())
    return {v["cveID"] for v in data.get("vulnerabilities", [])}


def run_scan(target: str) -> list[dict]:
    """Runs Trivy against a target (image, filesystem, repo). Requires
    trivy installed and on PATH."""
    result = subprocess.run(
        ["trivy", "image", "--format", "json", target],
        capture_output=True, text=True, timeout=600,
    )
    parsed = json.loads(result.stdout)
    findings = []
    for res in parsed.get("Results", []):
        for vuln in res.get("Vulnerabilities", []):
            findings.append({
                "cve_id": vuln.get("VulnerabilityID"),
                "package": vuln.get("PkgName"),
                "cvss": vuln.get("CVSS", {}),
            })
    return findings


def prioritize(client: ModelClient, findings: list[dict], kev_set: set[str],
                asset_criticality: str) -> list[PatchPriority]:
    for f in findings:
        f["known_exploited"] = f["cve_id"] in kev_set
    response = client._call_raw(
        system=PRIORITIZE_SYSTEM_PROMPT,
        user_content=json.dumps({
            "findings": findings,
            "asset_criticality": asset_criticality,
        }),
    )
    parsed = json.loads(response)
    return [PatchPriority(**item) for item in parsed]


def main(target: str, asset_criticality: str = "internet-facing"):
    client = ModelClient(provider="openai", model="gpt-5.6-sol")

    kev_set = fetch_kev_catalog()
    findings = run_scan(target)
    prioritized = prioritize(client, findings, kev_set, asset_criticality)

    patch_now = [p for p in prioritized if p.priority == "patch_now"]
    print(f"{len(patch_now)} findings need patching now")
    for p in patch_now:
        print(f"  - {p.cve_id}: {p.reasoning}")

    with open("./priority_digest.jsonl", "a") as f:
        for p in prioritized:
            record = p.model_dump()
            record["scanned_at"] = datetime.now(timezone.utc).isoformat()
            f.write(json.dumps(record) + "\n")


if __name__ == "__main__":
    main(target="your-image:latest")  # replace with your actual target
