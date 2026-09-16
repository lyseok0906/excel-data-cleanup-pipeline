# V2 Schema Validation — 10-Site Pilot: Productivity Software & PKM Content Niche

**Date of research:** 2026-09-16
**Purpose:** QA/validation of the V2 field schema (value/evidence/note triplets) against real, currently-active content sites. Not intended to support any market conclusion.

## Niche and sampling design

Niche: Productivity software & personal knowledge management (PKM) content — Notion, Obsidian, Todoist, PARA, Zettelkasten, task management, personal productivity systems. This niche was not covered by the prior 100-site (mostly Excel/tech-tips) study, and none of the 10 sites below overlap with the excluded domain list.

Applied the 4-layer "Contrast Cohort" sampling design:

| Layer | Sites chosen |
|---|---|
| Large / Traffic Leader | thomasjfrank.com, zapier.com, asianefficiency.com |
| Mid-scale Active Site | nesslabs.com, keepproductive.com |
| Narrow Niche Authority | fortelabs.com, zettelkasten.de, linkingyourthinking.com |
| Contrast Cohort | 43folders.com, zenhabits.net |

## Why each site fits its layer

- **thomasjfrank.com** — Large personal-brand site: 2.9M-subscriber YouTube channel feeding a Notion-template business with self-reported ~$175K/month recent revenue and $2.1M in template sales over 2021-2023 (Starter Story interview). Highest self-reported revenue in the sample.
- **zapier.com** (blog) — Largest raw traffic in the sample by a wide margin (~5.3M visits/3mo, whole-domain Similarweb figure). Included deliberately as an edge case: it's a company blog on a SaaS product's main domain, not an independent content site, which stress-tests whether the schema can represent "traffic measured includes non-blog product/app traffic, revenue not separable from the company" cleanly (see Ambiguity section below).
- **asianefficiency.com** — 14+ years old (since 2011), 50,000+ stated newsletter subscribers, broad press mentions (Forbes, Fast Company, The Guardian), diversified monetization (courses, coaching, workshops, podcast). Placed in Large/Traffic Leader on brand longevity and audience size grounds even though its *measured* current traffic (~12K/mo via Similarweb) is lower than several sites classified in narrower layers — flagged explicitly as an ambiguous fit (see below).
- **nesslabs.com** — Solid mid-scale traffic (~90K/mo), single-operator (Anne-Laure Le Cunff) newsletter-and-book model, actively growing per Similarweb (+15.87% MoM at lookup).
- **keepproductive.com** — Long-running (since 2017, YouTube presence since 2011), multi-product monetization (course, own iOS app, affiliate deals, advisory stakes), but traffic could not be independently confirmed (Similarweb returned no data; robots.txt blocked direct homepage verification) — placed in Mid-scale on the strength of documented monetization/operating history rather than confirmed traffic, and this gap is itself flagged as a QA finding.
- **fortelabs.com** — Originating home of the PARA Method / "Building a Second Brain" framework, a specific, globally recognized sub-methodology within PKM. Chosen for topical authority/originality rather than traffic size (its traffic, ~94K/mo, actually exceeds asianefficiency.com's).
- **zettelkasten.de** — The definitive site for the Zettelkasten method specifically, run by co-authors of the reference book on the topic, with its own commercial app ("The Archive"). Narrow, singular topical scope.
- **linkingyourthinking.com** — Nick Milo's "LYT" is a specific, named PKM sub-methodology distinct from Zettelkasten/PARA, with deep authority inside the Obsidian community and high-ticket workshops ($1,499-$4,500). Traffic surging (+34.69% MoM) at lookup, plausibly tied to a recently reported book deal.
- **43folders.com** — Contrast Cohort: originally one of the most influential early GTD/productivity blogs (founded 2004 by Merlin Mann), now a fully parked domain (direct fetch 302-redirects to a generic "This domain has no active website" parking page). Similarweb traffic collapsed to ~4K/3mo with a 58.36% MoM drop. This is the clearest possible decline case: total shutdown, not just reduced cadence.
- **zenhabits.net** — Contrast Cohort: Time magazine's "Top 25 Blogs" in 2009 and 2010 (peak era), founded 2007, still active and still monetizing (books, coaching, an academy program), but Similarweb shows a verified multi-month decline — global rank worsening from #133,150 to #142,017 over the trailing 3 months and a -4.89% MoM drop at the most recent reading. Chosen deliberately alongside 43folders.com to represent the milder "historically strong, now measurably declining" pattern versus 43folders.com's "fully dead" pattern — two different flavors of Contrast Cohort evidence.

## Sites considered and rejected

- **notion.so/blog**, **todoist.com/blog** — rejected as company/product blogs too close in kind to zapier.com (already included as the one "company blog" edge case); including more than one would have made the sample redundant for that particular ambiguity rather than adding new signal.
- **productivityist.com** (Mike Vardy) — considered for Contrast Cohort; search results suggested reduced activity, but I could not obtain strong direct verification (traffic tool data, or a clear operator statement) within this pass, so I substituted zenhabits.net, which had stronger, more directly verifiable evidence (Wikipedia-documented peak + Similarweb-documented measured decline).
- **notionmastery.com** (Marie Poulin) and **redgregory.com** — considered for Narrow Niche Authority; passed over in favor of zettelkasten.de and linkingyourthinking.com, which had clearer first-party/operator-level founding evidence and more directly observable monetization signals on the pages fetched.
- **lifehack.org** — excluded per the brief's general-purpose/aggregator exclusion spirit (broad multi-topic content site, not focused on PKM/productivity systems specifically, and closer in kind to the already-excluded makeuseof.com/howtogeek.com style sites).
- **thesweetsetup.com** — considered for Mid-scale; passed over for keepproductive.com because keepproductive.com had clearer, citable third-party documentation (theplus.so profile) of specific monetization mechanics (affiliate deals, an owned app, a named course), which made for a more informative schema test case, particularly around the "traffic UNKNOWN but monetization well-documented" ambiguity.

## Ambiguities hit while applying the Y/N/UNKNOWN + A/B/C/D schema

1. **"Traffic value" for a company blog on a product's main domain (zapier.com).** Similarweb only reports whole-domain traffic, which necessarily includes app/product traffic, not just blog readership. The schema has no field to flag "this traffic figure is not blog-attributable" other than a free-text note — worth considering a dedicated boolean like `traffic_includes_non_blog_domain` in a future schema revision.

2. **Evidence tier for interview-reported operator figures (thomasjfrank.com revenue).** Thomas Frank's revenue figures were reported by him directly, but published via a third-party interview site (Starter Story), not his own site. I coded this as A ("operator self-published figure") on the reasoning that the numbers are directly attributed to the operator in his own words, not a third party's estimate — but a case could be made for B instead, since the *publication* is third-party. This ambiguity (self-reported-via-third-party-interview) recurred and should probably get explicit schema guidance, since it is very common in creator-economy research (Starter Story, podcast interviews, etc. are a primary source of "revenue" data for solo operators).

3. **Distinguishing "no ads present" as an operator claim (A) vs. an observation (C).** For zenhabits.net, Leo Babauta explicitly states on his About page "I don't take... advertising" — this is simultaneously an operator statement (evidence A) and something I could also just observe directly (evidence C, no ad units seen). I used A here since it was an explicit first-party claim, but flag that a field could plausibly get either tier depending on which fact is treated as primary; guidance on precedence (self-statement beats direct observation, or vice versa) would help consistency.

4. **`is_contrast_case` note field forced two different kinds of decline into one field.** 43folders.com (total shutdown, domain now parked) and zenhabits.net (still active, but measurably declining vs. historic peak) are qualitatively very different kinds of "contrast" evidence, yet the schema's `is_contrast_case` is a flat Y/N with a single free-text note. This worked adequately since the note field could carry the nuance, but a future version might benefit from a `contrast_pattern` enum (e.g. `shutdown` / `cadence_drop` / `traffic_decline` / `low_traction_despite_age`) so this doesn't all collapse into freeform text.

5. **`traffic_value` units when Similarweb reports "trailing 3 months total" rather than a monthly figure.** All Similarweb free-tier pages I could access showed a 3-month total rather than a clean single-month number. I recorded the 3-month total as `traffic_value` and used `traffic_note` to state the implied monthly figure and the exact metric period, per the schema's `traffic_metric` field — but this means `traffic_value` is not uniformly "monthly visits" across every prior/future dataset unless every researcher is careful to normalize it. Worth adding an explicit normalization rule (e.g. "always report monthly-equivalent, note the raw source period") to the protocol.

6. **UNKNOWN vs. inferred-N for absence of a signal (e.g., affiliate on zettelkasten.de, linkingyourthinking.com).** When I fetched a homepage and saw no affiliate disclosures, I had to decide between `N` (evidence D, inferred from absence) and `UNKNOWN` (since absence-of-evidence on one page isn't proof of site-wide absence). I used N/D when the site's overall monetization model made an affiliate program implausible (e.g., a site selling its own $1,500 workshops or its own $250 course has little incentive to also run affiliate links, and none were seen across multiple pages), but UNKNOWN when the omission felt more like a gap in my access (e.g., asianefficiency.com's affiliate status, keepproductive.com blocked by robots.txt). This judgment call should be made more explicit in the protocol — perhaps a rule like "N/D is permitted only after checking at least 2 distinct pages (home + one content/monetization page) with no affiliate signal; a single homepage check with no signal should be UNKNOWN."

## Tools used

- WebSearch (general search)
- WebFetch against: Similarweb public overview pages (traffic), operator "About" pages, Wikipedia, MetaFilter, Starter Story, and third-party creator-profile sites (theplus.so)

All traffic figures are Similarweb free-tier estimates (directional only, not exact); all revenue figures are either operator self-reports via interview or marked UNKNOWN — no revenue numbers were fabricated or estimated by the researcher.
