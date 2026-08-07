[POST BODY — paste directly, link goes in first comment, not here]

A vulnerability caught in a quarterly pentest already shipped months
earlier. The tool that finds it once a quarter is the same tool that
could've caught it before merge — the only difference is timing.

Module 5: SAST/DAST + OWASP Top 10, running on every commit instead of
once a quarter.

→ Semgrep (free, OSS) does static analysis on every commit — fast
enough to run in CI without anyone noticing the pipeline got slower.

→ OWASP ZAP does dynamic analysis against staging — never production,
that line matters and I'll say it again in the full writeup.

→ An agent dedupes findings, classifies each one against the actual
OWASP Top 10 category, and flags which are safe to draft a fix for
automatically. "Safe" is a high bar here: mechanical, low-risk changes
only — never anything touching auth logic.

→ Every fix PR still requires human review before merge. No exceptions,
regardless of how confident the classification is.

The honest cost note on this one: it's one of the higher-volume modules
in the series, so budget for LLM inference scaling with your commit
volume, not CSPM-level costs. Still meaningfully cheaper than
Snyk/Checkmarx-class platforms if you have the AppSec expertise
in-house to tune the rulesets — and the verdict says clearly when you
don't.

Full build + code linked below.

#Security #AI #Agentic #DevSecOps #BuildVsBuy #CyberSecurity #AppSec #SGIConsent #GenerativeAI #AIAssisted
