# AgenticSecOps: Build vs. Buy

**A build-vs-buy series on replacing (or informing a decision not to
replace) MSSP/vendor security services with in-house AI agents.**

Managed security vendors — MDR, SOC-as-a-service, compliance automation,
pentesting-as-a-service — have proliferated over the last five years,
largely by bundling existing tools with a human/orchestration layer on
top. This series documents, module by module, what it actually takes to
build the AI-agent equivalent in-house: the architecture, the real build
and run cost, the risk if something is missed, which LLM fits which task,
and — most importantly — an honest verdict on whether building it
yourself is actually the right call for your organization's size and
maturity.

Some modules conclude "build it, here's how." Others conclude "buy it,
and here's exactly why the math doesn't favor DIY." Both are useful
answers, and this series doesn't default to one over the other.

New module every **Wednesday, 9AM PST**. Follow along here or on
[LinkedIn](#) *(link to be added)*.

Repo: [github.com/nicklesh/AgenticSecOps-BuildVsBuy](https://github.com/nicklesh/AgenticSecOps-BuildVsBuy)

## Before you use anything here

Read [DISCLAIMER.md](./DISCLAIMER.md) first. Short version: this is
educational content, provided as-is, not professional security advice —
code samples are unvalidated starting points, not vetted tools, use is
at your own discretion — and anything resembling testing or attack
simulation must only ever be run against systems you own or are
explicitly authorized to test.

## Module Index

| # | Module | Status | What it covers |
|---|--------|--------|-----------------|
| 0 | [Foundations](./00-foundations) | **Shipped** | Model-abstraction pattern, eval-harness design, and the authorization/legal baseline every other module builds on |
| 1 | [GRC / Compliance Evidence Agent](./01-grc-compliance) | **Shipped** | Continuous control-evidence collection for SOC 2 / HIPAA / ISO |
| 2 | [Attack Surface Management (ASM) Agent](./02-asm) | **Shipped** | Continuous external asset discovery and exposure tracking |
| 3 | [CSPM Agent](./03-cspm) | **Shipped (pilot module)** | Cloud config drift detection against CIS benchmarks |
| 4 | [Vulnerability Prioritization & Patch Agent](./04-vuln-patch) | **Shipped** | CVE triage against exploit-in-the-wild data and asset criticality |
| 5 | [SAST/DAST + OWASP Top 10 Agent](./05-sast-dast) | **Shipped** | Continuous code and app scanning integrated into CI/CD |
| 6 | [Identity & Access Review Agent](./06-identity-access) | **Shipped** | Continuous IAM review, stale/excess privilege detection |
| 7 | [Phishing Simulation & Awareness Agent](./07-phishing-sim) | **Shipped** | Simulated phishing campaigns and targeted training |
| 8 | [Breach & Attack Simulation Agent](./08-bas-redteam) | **Shipped** | Detection-validation against MITRE ATT&CK (architecture + pseudocode only — see disclaimer) |
| 9 | [Autonomous Pentest Agent](./09-autonomous-pentest) | Coming soon | Why this is the one module where "buy" is the default answer (architecture + pseudocode only — see disclaimer) |
| 10 | [SOC Alert-Triage Agent](./10-soc-triage) | Coming soon | Automated alert investigation and verdict drafting |

## What each module includes

- Problem framing and the real cost of missing it (with liberal vs.
  worst-case figures)
- Architecture diagram and data flow
- **Code status disclaimer** — an explicit callout near the top of every
  module stating the code is unvalidated, provided to illustrate
  approach, and used at the reader's own discretion (see
  [DISCLAIMER.md](./DISCLAIMER.md))
- Build walkthrough (real runnable starter code for modules 1–7 and 10;
  architecture + pseudocode only for modules 8–9)
- Autonomous / human-approval-required / vendor-territory boundaries for
  what the agent should and shouldn't do unsupervised
- Eval and KPI checklist — how to know if your build is actually working
- Cost model — build cost, run cost, and vendor-equivalent pricing
- LLM recommendation and swap-readiness notes
- A closing build-vs-buy verdict

## License

[MIT](./LICENSE), with additional educational-use terms in
[DISCLAIMER.md](./DISCLAIMER.md).
