"""
CSPM Draft-PR Step
Intentionally a separate script from agent.py. Running the triage and
opening PRs are two different decisions — don't chain them into one
automatic pipeline. Every PR opened here is marked draft=True and
requires manual review and merge.

Usage (after agent.py has produced triage_output.json):
    python draft_pr.py
"""

import json
import os
from github import Github  # PyGithub


def open_draft_pr(finding: dict, repo_name: str, gh_token: str):
    gh = Github(gh_token)
    repo = gh.get_repo(repo_name)
    branch_name = f"cspm-fix/{finding['group_id']}"

    # In a real implementation: create the branch and apply the specific
    # Terraform/CloudFormation/config change here, then commit it.
    # Left as an exercise per your own IaC tooling — the point of this
    # module is the triage/decision layer, not reinventing your deploy
    # pipeline.

    repo.create_pull(
        title=f"[CSPM] {finding['summary']}",
        body=(
            f"Auto-drafted by CSPM triage agent.\n\n"
            f"**Remediation:**\n{finding['remediation_steps']}\n\n"
            f"**Affected resources:** {finding['affected_resources']}\n\n"
            f"⚠️ Review before merging — this was drafted, not verified, "
            f"by the agent."
        ),
        head=branch_name,
        base="main",
        draft=True,
    )


def main():
    gh_token = os.environ["GITHUB_TOKEN"]
    repo_name = os.environ.get("GITHUB_REPO", "your-org/infra")

    with open("./triage_output.json") as f:
        triaged = json.load(f)

    for finding in triaged:
        if finding["auto_draftable"]:
            open_draft_pr(finding, repo_name=repo_name, gh_token=gh_token)


if __name__ == "__main__":
    main()
