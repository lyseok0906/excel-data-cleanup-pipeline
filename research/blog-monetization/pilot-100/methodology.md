# Methodology — 100-Site Blog Monetization Pilot Study

## Purpose and scope

This pilot compiled publicly available evidence on 100 content sites (10 categories x 10 sites each) to look for patterns in how independent or independent-origin content sites monetize, as background research for a new site, CleanSheetHQ, in the "Excel Data Cleanup & Transformation" niche. The compilation below synthesizes ten research batches that were already gathered by separate research passes; no new web research, estimation, or invention of figures was performed while assembling `sites.csv`, `findings.md`, or this document. Every number, evidence tier, and qualitative label in the four deliverable files traces back to a specific source file cell or footnote from those ten batches.

## Evidence-tier system

Each factual claim (traffic, revenue, monetization structure, dates) carries one of five evidence codes, used consistently across the ten source batches and preserved unchanged into `sites.csv`:

- **A — Operator self-published.** The site owner, founder, or their own company page/report/interview directly states the figure in their own words (e.g., a blog's own monthly income report, an "About" page's self-reported download count, a founder's own income-report archive).
- **B — Credible third-party estimate or reporting.** A third-party tool (most often Similarweb, sometimes Semrush) estimating traffic, or reputable press/trade coverage (Forbes, CNBC, Poynter, Variety, business-wire acquisition announcements) reporting a figure about the company. Traffic-estimation tools are directional, not exact, and can disagree with each other or with a site's own self-reported numbers (flagged explicitly where this occurred, e.g., Guiding Tech).
- **C — Monetization structure directly observed.** Not a number, but a monetization mechanism (e.g., "has a visible paywall," "displays ad units," "sells a downloadable file") confirmed by directly viewing site structure, disclosure pages, or advertiser/media-kit pages during the research pass.
- **D — Reasonable inference.** A conclusion drawn from general business-model knowledge, indirect signals, or a source that is not itself definitive (e.g., a third-party influencer-valuation site, an "About page implies X" inference). Always explicitly labeled D in the source tables and carried through as such.
- **UNKNOWN — No credible evidence found.** Used whenever a field could not be confirmed by any of the above tiers. This is the single most common value across the revenue-related columns in the dataset and must never be silently treated as "No" or "$0" (see Denominator Rule below).

Where a single cell mixes evidence types (e.g., "traffic B, revenue UNKNOWN"), both are preserved in `evidence_confidence` or in the paired `_evidence` column.

## Winner-type taxonomy

Each site was assigned one (or a combined) winner-type label by its originating research batch, used to characterize its primary basis for inclusion as a notable case:

- **TRAFFIC WINNER** — stands out primarily for raw visitor/pageview volume relative to its category, regardless of confirmed revenue.
- **REVENUE WINNER** — has directly-documented revenue figures (via income report, interview, or financial filing) that are unusually strong or well-evidenced for the category.
- **NICHE AUTHORITY** — long-tenured, deeply specialized site whose primary distinguishing trait is topical depth/authority rather than scale or disclosed revenue.
- **FAST-GROWTH WINNER** — documented rapid growth in a short window (traffic, revenue, or both), regardless of current absolute scale.
- Combined labels (e.g., "TRAFFIC WINNER / REVENUE WINNER," "NICHE AUTHORITY (small)," "NICHE AUTHORITY (financially fragile, contrast case)") were preserved verbatim from source batches, including cases intentionally included as *negative or contrast examples* (e.g., Backyard Boss, Modern Farmer) rather than success stories — these are flagged in their `notes`/appendix text and must not be read as endorsed monetization models.

## Batching process actually used

Ten categories were each assigned to a separate research subagent, working in parallel, with instructions to identify roughly 10 notable, currently active, independently-operated (or independent-origin) content sites per category and document a fixed set of fields per site using publicly available sources (Similarweb/Semrush traffic tools, founder interviews, press coverage, self-published income reports, company disclosures, and direct site inspection). Each batch subagent applied the same exclusion criteria:

- No personal diary blogs with no monetization structure.
- No large news organizations sampled as subjects (a large-media-owned property was acceptable as a *comparator or contrast case* if the underlying site began as or resembles an independent blog, but pure newsroom properties were excluded).
- No Amazon or other marketplace listings.
- No retailer/e-commerce company blogs (a blog whose entire purpose is marketing an e-commerce storefront's own inventory).

This compilation (the current task) then normalized the ten batches' differing table formats (extra "#" columns, footnote-marker conventions, Korean-language field values in the Product Review/Buying Guides batch, compact vs. expanded schemas) into the single `sites.csv` schema and the accompanying narrative documents, without adding, removing, or re-estimating any site or figure beyond what each batch already reported.

## Research Protocol Issues (substitutions and exclusions log)

The following substitutions and exclusions were made by the original batch subagents, for the stated reasons, and are preserved here for transparency. All final substituted sites are the ones present in `sites.csv`.

1. **Software/Tech Tutorials batch — TechJunkie excluded.** TechJunkie's traffic (~40K/mo) was judged too thin as a comparator against the other 10 verified candidates and was dropped in favor of a stronger candidate set.
2. **Software/Tech Tutorials batch — Guiding Tech's claimed Zoho ownership dropped.** An earlier candidate list asserted Guiding Tech was Zoho-owned; the batch subagent investigated and found no evidence for this (the site self-describes as the independent "Guiding Tech Media"). The ownership claim was dropped; the site itself was kept in the sample.
3. **Home/DIY batch — Fix.com excluded, substituted with A Beautiful Mess.** Fix.com is the blog of an appliance-parts e-commerce retailer, which directly violates the retailer-blog exclusion rule. It was replaced with A Beautiful Mess (home vertical) to fill the "fast-growth / diversified brand" slot.
4. **Food/Recipe batch — The Pioneer Woman excluded, substituted with Once Upon a Chef.** The Pioneer Woman (thepioneerwoman.com) operates under Hearst Magazine Media's corporate publishing/TV/retail infrastructure, making it a corporate media brand rather than an independent solo-operator blog, breaking comparability with the rest of the set. Once Upon a Chef (Jenn Segal) — independent, large-scale, documented via a Google Ads Publisher case study — was substituted.
5. **Travel batch — Legal Nomads and Man vs Debt excluded, substituted with Travel Lemming and The Planet D.** Legal Nomads has pivoted almost entirely away from travel into chronic-illness/grief content and runs ad-free/Patreon-funded, no longer fitting the travel-monetization comparison; Man vs Debt is fundamentally a personal-finance blog with only tangential travel framing and has been semi-dormant since the founder's 2012 "retirement." Both were replaced with Travel Lemming (active, well-documented FAST-GROWTH WINNER) and The Planet D (active, awards-backed NICHE AUTHORITY).
6. **Product Review/Buying Guides batch — The Spruce Eats excluded, substituted with Reviewed.com.** The Spruce Eats is food-focused and was judged not to fit the "independent buying-guide" comparator set as well as a general consumer-product review site; Reviewed.com was substituted.

### Additional caveats disclosed inside individual source batches

- **Gardening/Outdoor batch — Gardener's Path traffic reading anomaly.** The Semrush traffic tool returned an unreliable "0" reading for gardenerspath.com; the site was independently confirmed active via direct fetch, and the traffic field is recorded as UNKNOWN (data gap) rather than 0.
- **Product Review/Buying Guides batch — Wirecutter domain-migration measurement issue.** Wirecutter's traffic can no longer be measured as an independent domain because it now lives at nytimes.com/wirecutter as an NYT subsection; the old thewirecutter.com domain's Similarweb reading is a redirect remnant and is recorded as reference-only, with the site's current independent traffic recorded as UNKNOWN.
- **Product Review/Buying Guides batch — mattress-review industry conflict-of-interest caveat.** The mattress-review industry (including Sleepopolis and Mattress Clarity, both in this sample) has had manufacturer-ownership/conflict-of-interest concerns raised in secondary sources; their claims of editorial independence were not taken at face value and are flagged in their notes rather than treated as confirmed.
- **Software/Tech Tutorials batch — Windows Central and Digital Trends data-quality flags.** Windows Central's -30.6% month-over-month traffic drop and Digital Trends' paywall-gated exact-visits figure (D-grade rather than B) are both flagged as lower-confidence data points warranting a follow-up check with a paid analytics tool before relying on them further.
- **Personal Finance batch — multiple UNKNOWN gaps flagged explicitly.** Root of Good's traffic/revenue, Wallet Hacks' revenue, The Points Guy's acquisition price and current revenue, The Financial Diet's current revenue, Mr. Money Mustache's revenue, and The Penny Hoarder's current (post-2016) figures and ownership status were all explicitly flagged as unconfirmed by that batch rather than estimated.
- **Excel/Spreadsheet/Productivity batch — Ablebits location and XelPlus revenue confidence.** Ablebits' Moldova/Belarus location is inferred from third-party business-listing sites (Owler/Tracxn/Ampliz), not independently confirmed (D). XelPlus's "$3M/year" figure is a single podcast claim, not independently corroborated, and is treated as B with lower confidence than other A/B figures in that batch.
- **Career/Education batch — inference-heavy monetization flags.** Fields marked (D) in that batch (e.g., several display_ads/affiliate flags) are reasonable inferences from visible site structure and general business-model knowledge, not independently verified line items, and should be weighted lower than (C)-flagged direct observations in the same batch.

### Cross-batch duplicate-domain issue (found during post-compilation QA, not caught during the original 10 parallel batches)

Because the 10 category batches ran independently and in parallel rather than sequentially with a shared running domain list, three domains were sampled twice under two different category labels, each time as a distinct vertical of the same underlying media brand:

- **thespruce.com** — sampled as "The Spruce" (Home/DIY) and separately as "The Spruce (Garden)" (Gardening/Outdoor).
- **bobvila.com** — sampled as "Bob Vila" (Home/DIY) and separately as "Bob Vila (Garden/Outdoor)" (Gardening/Outdoor).
- **thepointsguy.com** — sampled as "The Points Guy" (Personal Finance) and separately as "The Points Guy" (Travel).

This means `sites.csv` contains 100 rows but only **97 unique root domains**. The rows are kept as-is (each row characterizes a genuinely different content vertical/section of the same brand, with different traffic/content notes in the source batches) rather than deleted, so as not to silently discard evidence already gathered — but any statistic computed "per unique operator" rather than "per content vertical" should use a denominator of 97, not 100, for these three brands. This is logged here per the user's required protocol (batching discipline: check for duplicate domains after each batch) rather than corrected retroactively by re-running batches, since the pilot's scope is closed.

## Denominator rule for all frequency statistics

Whenever this study (in `findings.md` or elsewhere) states a frequency statistic of the form "X of Y sites do [something]," Y is always the count of sites in the relevant category or full sample that have a **CONFIRMED, non-UNKNOWN** value for that specific field — never the full 100-site or full-category count unless every site in that group actually has a confirmed value. UNKNOWN must never be silently treated as "No," "false," or "$0." Any statistic that does not state its denominator explicitly should be treated as an error in that document, not as license to assume UNKNOWN = No elsewhere.

## Known limitations of this pilot

- **Traffic tools are not directly comparable to one another.** Similarweb, Semrush, and self-reported operator numbers use different methodologies (unique visitors vs. visits vs. pageviews, different sampling/panel methods, different definitions of "monthly"), and figures from different tools should not be treated as apples-to-apples even within the same table row, let alone across sites measured by different tools.
- **Single-source revenue claims are not independently audited.** The large majority of revenue figures in this dataset come from a single founder interview, podcast, or self-published income report; only NerdWallet (SEC 10-K filings) and Family Handyman (an operator media kit, self-reported but detailed) have anything resembling audited or formally disclosed financials. All other revenue figures should be treated as directionally informative, not verified.
- **Revenue is disproportionately UNKNOWN.** Across the 100-site sample, confirmed (non-UNKNOWN) revenue figures exist for a minority of sites; the majority of monetization conclusions in `findings.md` necessarily rest on monetization-*structure* observations (ads present, affiliate links present, paywall present) rather than confirmed dollar amounts, and this is stated explicitly wherever a revenue-based claim is made.
- **Traffic snapshots are single-point-in-time (accessed Sept 2026)** and several show sharp month-over-month swings (e.g., Windows Central -30.6%, Halfway Anywhere -24%, Section Hiker +21%) that may reflect real trend, seasonal variation, algorithm changes, or tool measurement noise — these are flagged individually where they occur rather than smoothed over.
- **Sample size per category (10 sites) is small** and was intentionally curated toward "notable" or currently-active sites rather than randomly sampled, so category-level patterns should be read as illustrative case evidence, not statistically representative of the full population of blogs in that niche.
- **Winner-type and evidence-confidence labels were assigned by each batch's own subagent** using consistent definitions but independent judgment calls; borderline classification differences between batches (e.g., what counts as "NICHE AUTHORITY" vs. "TRAFFIC WINNER") were not re-adjudicated in this compilation pass.
