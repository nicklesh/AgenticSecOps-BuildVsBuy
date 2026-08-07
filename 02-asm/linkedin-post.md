[POST BODY — paste directly, link goes in first comment, not here]

You can't secure what you don't know you have.

A forgotten staging subdomain. A demo S3 bucket from eight months ago.
Marketing's old microsite still pointed at a live server. These
accumulate silently — and most companies find out about one the same
way an attacker does: by it being exposed.

Module 2: Attack Surface Management. Probably the cheapest, lowest-risk
module in this whole series to build yourself.

→ Amass and Subfinder (both free, both OSS) do the actual subdomain
enumeration. Shodan/Censys cover exposed services beyond DNS.

→ An agent diffs today's scan against your last known inventory and
classifies what changed: known, needs review, or anomaly.

→ Anomalies get flagged immediately — an exposed admin panel, a
database port that shouldn't be internet-facing, a naming pattern that
screams "forgotten dev environment."

The whole thing is read-only. It doesn't touch your infrastructure, it
just tells you what's already visible to anyone who looks. That's why
this is one of the few modules in the series I'd recommend building
regardless of company stage — even pre-seed, if you have any external
surface worth tracking.

Build cost: ~$10K, 2-4 weeks. Run cost: under $350/month even with paid
API tiers. Compare that to a vendor ASM tool at $1-3K/month, or to what
it costs when someone else finds your exposed asset first — $3.31M
average breach cost, more if ransomware follows.

Full build + code linked below.

#security #ai #agentic #devsecops #buildvsbuy
