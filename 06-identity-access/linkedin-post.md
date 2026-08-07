[POST BODY — paste directly, link goes in first comment, not here]

The account that gets compromised is rarely the one everyone's
watching. It's the one nobody remembered to review — the support
agent with leftover database admin access, the contractor whose
account outlived the contract, the integration provisioned with far
more scope than it actually uses.

Module 6: the identity and access review agent.

→ Pulls role assignments, last-login data, and department context
straight from your IdP — Okta or Entra ID.

→ Flags four things: stale (no login in 90+ days), excessive (scope
doesn't match the job), orphaned (no clear owner), or ok.

→ Here's the part I want to be explicit about: this agent never
revokes anything. Every output is a proposal for a human to review — a
wrongly revoked production service account is an outage, and that's a
worse failure mode than a missed review.

The build is small — about $10K, 2-3 weeks — because the real cost
isn't engineering, it's the discipline of holding that human-gate every
single time, especially once it feels "obviously safe" to auto-approve
the low-risk ones. Don't.

Verdict: build this at almost any company stage. The one exception is
regulated environments needing formal SOX-style attestation — that's
where a dedicated IGA platform's audit trail earns its enterprise price
tag over a DIY report.

Full build + code linked below.

#Security #AI #Agentic #DevSecOps #BuildVsBuy #CyberSecurity #AppSec #SGIConsent #GenerativeAI #AIAssisted
