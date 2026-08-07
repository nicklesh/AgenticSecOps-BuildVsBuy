[POST BODY — paste directly, link goes in first comment, not here]

Before I show you how to build any of the 10 security agents in this
series, one confession: the first version I built was welded to a
single LLM provider. Swapping models would've meant a rewrite, not a
config change.

That's Module 0 — the foundation every other module in this series
builds on, published before module 4 because it should've been in
module 1.

Three things worth building once, not ten times:

→ A provider-agnostic call layer. Route every agent's LLM calls through
one thin wrapper instead of importing a vendor SDK directly into your
logic. The provider becomes a config value.

→ Structured output enforced by schema, not by trusting model
behavior. Every finding, verdict, or ranked list validates against a
fixed contract regardless of which model produced it — so your
dashboard and your ticketing integration don't break on a model swap.

→ A golden eval set per module, checked before every cutover. This is
the part people skip. Without it, "easy to switch models" quietly
becomes "switched, and regressed your false-negative rate for three
weeks before anyone noticed."

The uncomfortable truth: today's "best" model for any given task will
not be best in two quarters. Build for that now, or rebuild for it
later.

Full pattern, code, and the eval harness are linked below.

#security #ai #agentic #softwarearchitecture #buildvsbuy
