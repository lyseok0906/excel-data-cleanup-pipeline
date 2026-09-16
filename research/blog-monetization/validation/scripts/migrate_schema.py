import csv

SRC = "/home/claude/research/blog-monetization-100/v2_validation/validation_10.csv"
DST = "/home/claude/research/blog-monetization-100/v2_validation/validation_10_v2.csv"

with open(SRC, newline='', encoding='utf-8') as f:
    old = {r['canonical_root_domain']: r for r in csv.DictReader(f)}

RESEARCH_DATE = "2026-09-16"  # ISO, single lookup session for all 10 rows

# Traffic tier thresholds (provisional, documented in protocol patch)
def traffic_tier(monthly):
    if monthly is None:
        return "UNKNOWN"
    if monthly >= 200000:
        return "HIGH"
    if monthly >= 20000:
        return "MID"
    return "LOW"

# Manually curated migration table built ONLY from data already present in validation_10.csv
# and validation_10_notes.md -- no new research performed.
rows_out = []

def base(domain):
    o = old[domain]
    return o

def bool_field(o, field, evidence_override=None, source_url="", note_extra=""):
    v = o[field].strip()
    ev = o[field + "_evidence"].strip()
    note = o[field + "_note"].strip()
    if evidence_override is not None:
        ev = evidence_override
    # Rule #8: UNKNOWN value -> UNKNOWN evidence, move any inference reasoning to note only
    if v == "UNKNOWN":
        ev = "UNKNOWN"
    if note_extra:
        note = (note + " " + note_extra).strip()
    return v, ev, source_url, note

# ---- Row-by-row migration ----

# 1. thomasjfrank.com
o = base("thomasjfrank.com")
rows_out.append(dict(
    canonical_root_domain="thomasjfrank.com", site_name="Thomas Frank",
    primary_niche=o["primary_niche"],
    sampling_stratum="Large/Traffic Leader",
    traffic_tier=traffic_tier(118600/3), is_niche_authority="N", is_niche_authority_evidence="D",
    is_niche_authority_source_url="", is_niche_authority_note="Large personal-brand/creator site; not the singular reference site for a named sub-methodology the way fortelabs.com/zettelkasten.de/linkingyourthinking.com are.",
    is_contrast_case="N", is_contrast_case_evidence="D", is_contrast_case_source_url="",
    is_contrast_case_note="Not a contrast case; used as Large/Traffic Leader example. The -25.66% MoM dip Similarweb reported is a single-month snapshot, not a verified multi-period decline.",
    contrast_pattern="NOT_APPLICABLE", contrast_evidence_period="",
    start_year_value="2010", start_year_evidence="B", start_year_source_url="https://www.starterstory.com/stories/thomas-frank",
    start_year_note="Started as 'College Info Geek' blog in 2010; pivoted the business around Notion templates starting 2021, per Starter Story interview.",
    traffic_provider="Similarweb", traffic_metric="total visits", traffic_scope="CONTENT_ONLY",
    traffic_value_raw="118600", traffic_value_raw_period="trailing_3_months",
    traffic_value_monthly_equivalent=str(round(118600/3)), traffic_normalization_method="raw_3mo_total / 3, rounded to nearest integer",
    traffic_research_date=RESEARCH_DATE, traffic_source_period="Similarweb snapshot dated August 2026",
    traffic_evidence="B", traffic_source_url="https://www.similarweb.com/website/thomasjfrank.com/",
    traffic_note="Global rank #345,634 at lookup; 25.66% MoM decline observed at time of lookup (single-month reading). Similarweb free-tier estimates are directional only.",
    revenue_value="~$175,000/month (recent), $2.1M over 2021-2023 from templates", revenue_figure_period="2021-2023 (cumulative), recent monthly figure as of 2023 interview",
    revenue_research_date=RESEARCH_DATE, revenue_evidence="A", revenue_source_url="https://www.starterstory.com/stories/thomas-frank",
    revenue_note="Self-reported by Thomas Frank in a Starter Story interview: ~$120K/mo template sales + ~$15K/mo affiliate/AdSense + $1,200/mo Pipedream affiliate. Coded A: figures attributed directly to the operator's own words, even though published via a third-party interview site.",
    **dict(zip(
        ["display_ads","display_ads_evidence","display_ads_source_url","display_ads_note",
         "affiliate","affiliate_evidence","affiliate_source_url","affiliate_note",
         "own_product","own_product_evidence","own_product_source_url","own_product_note",
         "course_or_community","course_or_community_evidence","course_or_community_source_url","course_or_community_note",
         "newsletter_email_capture","newsletter_email_capture_evidence","newsletter_email_capture_source_url","newsletter_email_capture_note"],
        [*bool_field(o,"display_ads"), *bool_field(o,"affiliate", source_url="https://www.starterstory.com/stories/thomas-frank"),
         *bool_field(o,"own_product"), *bool_field(o,"course_or_community"), *bool_field(o,"newsletter_email_capture")]
    ))
))

# 2. zapier.com
o = base("zapier.com")
rows_out.append(dict(
    canonical_root_domain="zapier.com", site_name="Zapier Blog",
    primary_niche=o["primary_niche"],
    sampling_stratum="Large/Traffic Leader",
    traffic_tier=traffic_tier(5300000/3), is_niche_authority="N", is_niche_authority_evidence="D", is_niche_authority_source_url="",
    is_niche_authority_note="Company content-marketing blog, not a singular named-methodology authority site.",
    is_contrast_case="N", is_contrast_case_evidence="D", is_contrast_case_source_url="",
    is_contrast_case_note="Not a contrast case; included as Large/Traffic Leader example, flagged as a company-blog edge case (see traffic_scope).",
    contrast_pattern="NOT_APPLICABLE", contrast_evidence_period="",
    start_year_value="2012", start_year_evidence="B", start_year_source_url="",
    start_year_note="Zapier itself was founded in 2011 (Y Combinator); the blog's content-marketing engine is widely dated to ~2012-2013 per third-party retrospectives.",
    traffic_provider="Similarweb", traffic_metric="total visits", traffic_scope="WHOLE_DOMAIN_INCLUDES_PRODUCT",
    traffic_value_raw="5300000", traffic_value_raw_period="trailing_3_months",
    traffic_value_monthly_equivalent=str(round(5300000/3)), traffic_normalization_method="raw_3mo_total / 3, rounded to nearest integer",
    traffic_research_date=RESEARCH_DATE, traffic_source_period="Similarweb snapshot dated August 2026",
    traffic_evidence="B", traffic_source_url="https://www.similarweb.com/website/zapier.com/",
    traffic_note="Figure is for the ENTIRE zapier.com domain (app + marketing site + blog combined), not blog traffic alone -- see traffic_scope=WHOLE_DOMAIN_INCLUDES_PRODUCT. Not comparable to CONTENT_ONLY rows in this dataset without adjustment.",
    revenue_value="UNKNOWN", revenue_figure_period="UNKNOWN",
    revenue_research_date=RESEARCH_DATE, revenue_evidence="UNKNOWN", revenue_source_url="",
    revenue_note="Blog-attributable revenue not separable from overall SaaS company revenue. Zapier is reported elsewhere as a large, profitable SaaS company, but no source attributes a figure to blog content specifically.",
    **dict(zip(
        ["display_ads","display_ads_evidence","display_ads_source_url","display_ads_note",
         "affiliate","affiliate_evidence","affiliate_source_url","affiliate_note",
         "own_product","own_product_evidence","own_product_source_url","own_product_note",
         "course_or_community","course_or_community_evidence","course_or_community_source_url","course_or_community_note",
         "newsletter_email_capture","newsletter_email_capture_evidence","newsletter_email_capture_source_url","newsletter_email_capture_note"],
        [*bool_field(o,"display_ads"), *bool_field(o,"affiliate"),
         *bool_field(o,"own_product"), *bool_field(o,"course_or_community"), *bool_field(o,"newsletter_email_capture")]
    ))
))

# 3. asianefficiency.com
o = base("asianefficiency.com")
rows_out.append(dict(
    canonical_root_domain="asianefficiency.com", site_name="Asian Efficiency",
    primary_niche=o["primary_niche"],
    sampling_stratum="Large/Traffic Leader",
    traffic_tier=traffic_tier(35700/3), is_niche_authority="N", is_niche_authority_evidence="D", is_niche_authority_source_url="",
    is_niche_authority_note="Broad time-management/productivity coaching brand, not the singular reference site for one named sub-methodology.",
    is_contrast_case="N", is_contrast_case_evidence="D", is_contrast_case_source_url="https://www.similarweb.com/website/asianefficiency.com/",
    is_contrast_case_note="Not formally flagged as contrast case in this pass, though measured traffic (~11.9K/mo, LOW tier) and a 19.37% MoM dip are notably weaker than its 14-year operating history and press mentions would suggest -- borderline; flagged for reconsideration alongside is_niche_authority/traffic_tier separation (sampling_stratum=Large/Traffic Leader but traffic_tier=LOW is exactly the kind of stratum/tier mismatch this schema field split is meant to surface).",
    contrast_pattern="NOT_APPLICABLE", contrast_evidence_period="",
    start_year_value="2011", start_year_evidence="B", start_year_source_url="",
    start_year_note="About page describes the blog/newsletter starting as a passion project in 2011 (founder Thanh Pham's personal productivity journey began 2008).",
    traffic_provider="Similarweb", traffic_metric="total visits", traffic_scope="CONTENT_ONLY",
    traffic_value_raw="35700", traffic_value_raw_period="trailing_3_months",
    traffic_value_monthly_equivalent=str(round(35700/3)), traffic_normalization_method="raw_3mo_total / 3, rounded to nearest integer",
    traffic_research_date=RESEARCH_DATE, traffic_source_period="Similarweb snapshot dated August 2026",
    traffic_evidence="B", traffic_source_url="https://www.similarweb.com/website/asianefficiency.com/",
    traffic_note="Global rank #889,548, 19.37% MoM decrease at time of lookup.",
    revenue_value="UNKNOWN", revenue_figure_period="UNKNOWN",
    revenue_research_date=RESEARCH_DATE, revenue_evidence="UNKNOWN", revenue_source_url="",
    revenue_note="No self-published income figures found; site reports 50,000+ newsletter subscribers as an audience-size proxy, not a revenue figure.",
    **dict(zip(
        ["display_ads","display_ads_evidence","display_ads_source_url","display_ads_note",
         "affiliate","affiliate_evidence","affiliate_source_url","affiliate_note",
         "own_product","own_product_evidence","own_product_source_url","own_product_note",
         "course_or_community","course_or_community_evidence","course_or_community_source_url","course_or_community_note",
         "newsletter_email_capture","newsletter_email_capture_evidence","newsletter_email_capture_source_url","newsletter_email_capture_note"],
        [*bool_field(o,"display_ads"),
         # Rule #8 fix: original was UNKNOWN,D -> must become UNKNOWN,UNKNOWN, reasoning moved to note
         *bool_field(o,"affiliate", note_extra="[schema patch] evidence downgraded from D to UNKNOWN per Rule #8 (UNKNOWN value must carry UNKNOWN evidence); the D-level inference reasoning is preserved here as context only, not as evidence backing."),
         *bool_field(o,"own_product"), *bool_field(o,"course_or_community"), *bool_field(o,"newsletter_email_capture")]
    ))
))
rows_out[-1]["affiliate_evidence"] = "UNKNOWN"  # enforce

# 4. nesslabs.com
o = base("nesslabs.com")
rows_out.append(dict(
    canonical_root_domain="nesslabs.com", site_name="Ness Labs",
    primary_niche=o["primary_niche"],
    sampling_stratum="Mid-scale Active Site",
    traffic_tier=traffic_tier(269100/3), is_niche_authority="N", is_niche_authority_evidence="D", is_niche_authority_source_url="",
    is_niche_authority_note="Newsletter-first creator brand covering mindful productivity broadly, not a singular named-methodology reference site.",
    is_contrast_case="N", is_contrast_case_evidence="D", is_contrast_case_source_url="",
    is_contrast_case_note="Not a contrast case; active and growing per Similarweb's positive MoM trend at lookup time.",
    contrast_pattern="NOT_APPLICABLE", contrast_evidence_period="",
    start_year_value="2018", start_year_evidence="D", start_year_source_url="",
    start_year_note="Exact founding date not confirmed on-site; multiple secondary creator-story profiles place launch around 2018. Inference, not first-party statement.",
    traffic_provider="Similarweb", traffic_metric="total visits", traffic_scope="CONTENT_ONLY",
    traffic_value_raw="269100", traffic_value_raw_period="trailing_3_months",
    traffic_value_monthly_equivalent=str(round(269100/3)), traffic_normalization_method="raw_3mo_total / 3, rounded to nearest integer",
    traffic_research_date=RESEARCH_DATE, traffic_source_period="Similarweb snapshot dated June 2026",
    traffic_evidence="B", traffic_source_url="https://www.similarweb.com/website/nesslabs.com/",
    traffic_note="Global rank #172,591, +15.87% MoM increase at time of lookup.",
    revenue_value="UNKNOWN", revenue_figure_period="UNKNOWN",
    revenue_research_date=RESEARCH_DATE, revenue_evidence="UNKNOWN", revenue_source_url="",
    revenue_note="No self-published revenue figures found on-site; third-party creator-economy interviews discuss growth strategy but not exact revenue.",
    **dict(zip(
        ["display_ads","display_ads_evidence","display_ads_source_url","display_ads_note",
         "affiliate","affiliate_evidence","affiliate_source_url","affiliate_note",
         "own_product","own_product_evidence","own_product_source_url","own_product_note",
         "course_or_community","course_or_community_evidence","course_or_community_source_url","course_or_community_note",
         "newsletter_email_capture","newsletter_email_capture_evidence","newsletter_email_capture_source_url","newsletter_email_capture_note"],
        [*bool_field(o,"display_ads"), *bool_field(o,"affiliate"),
         *bool_field(o,"own_product"), *bool_field(o,"course_or_community"), *bool_field(o,"newsletter_email_capture")]
    ))
))

# 5. keepproductive.com
o = base("keepproductive.com")
rows_out.append(dict(
    canonical_root_domain="keepproductive.com", site_name="Keep Productive",
    primary_niche=o["primary_niche"],
    sampling_stratum="Mid-scale Active Site",
    traffic_tier="UNKNOWN", is_niche_authority="N", is_niche_authority_evidence="D", is_niche_authority_source_url="",
    is_niche_authority_note="Notion/productivity app review creator, not a singular named-methodology reference site.",
    is_contrast_case="N", is_contrast_case_evidence="D", is_contrast_case_source_url="",
    is_contrast_case_note="Not treated as contrast case; content/YouTube channel appear ongoing per search hits, but this is an inference given incomplete direct access (robots.txt blocked).",
    contrast_pattern="NOT_APPLICABLE", contrast_evidence_period="",
    start_year_value="2017", start_year_evidence="A", start_year_source_url="",
    start_year_note="Founder Francesco D'Alessio quoted directly: 'We started Keep Productive in late 2017, after 3 previous years on YouTube.'",
    traffic_provider="Similarweb", traffic_metric="total visits", traffic_scope="UNKNOWN",
    traffic_value_raw="UNKNOWN", traffic_value_raw_period="UNKNOWN",
    traffic_value_monthly_equivalent="UNKNOWN", traffic_normalization_method="UNKNOWN",
    traffic_research_date=RESEARCH_DATE, traffic_source_period="UNKNOWN",
    traffic_evidence="UNKNOWN", traffic_source_url="https://www.similarweb.com/website/keepproductive.com/",
    traffic_note="Similarweb free overview returned 'No Data to Display'; robots.txt also blocked direct site fetch. Genuinely unknown from available tools -- left UNKNOWN per schema rules rather than guessed.",
    revenue_value="UNKNOWN", revenue_figure_period="UNKNOWN",
    revenue_research_date=RESEARCH_DATE, revenue_evidence="UNKNOWN", revenue_source_url="",
    revenue_note="No self-published revenue figures found.",
    **dict(zip(
        ["display_ads","display_ads_evidence","display_ads_source_url","display_ads_note",
         "affiliate","affiliate_evidence","affiliate_source_url","affiliate_note",
         "own_product","own_product_evidence","own_product_source_url","own_product_note",
         "course_or_community","course_or_community_evidence","course_or_community_source_url","course_or_community_note",
         "newsletter_email_capture","newsletter_email_capture_evidence","newsletter_email_capture_source_url","newsletter_email_capture_note"],
        [*bool_field(o,"display_ads"), *bool_field(o,"affiliate", source_url="https://www.theplus.so"),
         *bool_field(o,"own_product", source_url="https://www.theplus.so"), *bool_field(o,"course_or_community", source_url="https://www.theplus.so"),
         *bool_field(o,"newsletter_email_capture")]
    ))
))

# 6. fortelabs.com
o = base("fortelabs.com")
rows_out.append(dict(
    canonical_root_domain="fortelabs.com", site_name="Forte Labs (Building a Second Brain / Tiago Forte)",
    primary_niche=o["primary_niche"],
    sampling_stratum="Narrow Niche Authority",
    traffic_tier=traffic_tier(281000/3), is_niche_authority="Y", is_niche_authority_evidence="D", is_niche_authority_source_url="",
    is_niche_authority_note="Originating source of the PARA Method / 'Building a Second Brain' framework specifically; globally recognized book/course franchise within the PKM sub-niche.",
    is_contrast_case="N", is_contrast_case_evidence="D", is_contrast_case_source_url="",
    is_contrast_case_note="Not a contrast case; traffic trending up per Similarweb at lookup time.",
    contrast_pattern="NOT_APPLICABLE", contrast_evidence_period="",
    start_year_value="2015", start_year_evidence="D", start_year_source_url="",
    start_year_note="Exact founding year not stated on fetched pages; inference from surrounding post dates and community history, not a first-party statement.",
    traffic_provider="Similarweb", traffic_metric="total visits", traffic_scope="CONTENT_ONLY",
    traffic_value_raw="281000", traffic_value_raw_period="trailing_3_months",
    traffic_value_monthly_equivalent=str(round(281000/3)), traffic_normalization_method="raw_3mo_total / 3, rounded to nearest integer",
    traffic_research_date=RESEARCH_DATE, traffic_source_period="Similarweb snapshot dated July 2026",
    traffic_evidence="B", traffic_source_url="https://www.similarweb.com/website/fortelabs.com/",
    traffic_note="Global rank #169,158, +5.19% MoM growth at time of lookup -- comparable to or higher than some Large-tier sites, illustrating traffic_tier and sampling_stratum need not align.",
    revenue_value="UNKNOWN", revenue_figure_period="UNKNOWN",
    revenue_research_date=RESEARCH_DATE, revenue_evidence="UNKNOWN", revenue_source_url="",
    revenue_note="No specific revenue figures found; a 2024 retrospective post references undisclosed 'sales milestones' for the book without numbers.",
    **dict(zip(
        ["display_ads","display_ads_evidence","display_ads_source_url","display_ads_note",
         "affiliate","affiliate_evidence","affiliate_source_url","affiliate_note",
         "own_product","own_product_evidence","own_product_source_url","own_product_note",
         "course_or_community","course_or_community_evidence","course_or_community_source_url","course_or_community_note",
         "newsletter_email_capture","newsletter_email_capture_evidence","newsletter_email_capture_source_url","newsletter_email_capture_note"],
        [*bool_field(o,"display_ads"),
         *bool_field(o,"affiliate", note_extra="[schema patch] evidence downgraded from D to UNKNOWN per Rule #8; original D-level inference (plausible affiliate links in 'best apps' content, not directly disclosed) preserved as context only."),
         *bool_field(o,"own_product"), *bool_field(o,"course_or_community"), *bool_field(o,"newsletter_email_capture")]
    ))
))
rows_out[-1]["affiliate_evidence"] = "UNKNOWN"  # enforce

# 7. zettelkasten.de
o = base("zettelkasten.de")
rows_out.append(dict(
    canonical_root_domain="zettelkasten.de", site_name="Zettelkasten Method (zettelkasten.de)",
    primary_niche=o["primary_niche"],
    sampling_stratum="Narrow Niche Authority",
    traffic_tier=traffic_tier(105500/3), is_niche_authority="Y", is_niche_authority_evidence="D", is_niche_authority_source_url="",
    is_niche_authority_note="Definitive, long-running reference site for the specific Zettelkasten method, run by co-authors of the reference book on the topic.",
    is_contrast_case="N", is_contrast_case_evidence="D", is_contrast_case_source_url="",
    is_contrast_case_note="Not a contrast case; growing traffic per Similarweb at lookup time.",
    contrast_pattern="NOT_APPLICABLE", contrast_evidence_period="",
    start_year_value="2013", start_year_evidence="D", start_year_source_url="",
    start_year_note="Exact launch date not stated on fetched pages; inferred from surrounding post dates and community history (Sascha Fast's biography post dated Dec 2014).",
    traffic_provider="Similarweb", traffic_metric="total visits", traffic_scope="CONTENT_ONLY",
    traffic_value_raw="105500", traffic_value_raw_period="trailing_3_months",
    traffic_value_monthly_equivalent=str(round(105500/3)), traffic_normalization_method="raw_3mo_total / 3, rounded to nearest integer",
    traffic_research_date=RESEARCH_DATE, traffic_source_period="Similarweb snapshot dated June 2026",
    traffic_evidence="B", traffic_source_url="https://www.similarweb.com/website/zettelkasten.de/",
    traffic_note="Global rank #395,998, +11.58% MoM growth; notably high 3m24s average visit duration suggesting an engaged niche readership.",
    revenue_value="UNKNOWN", revenue_figure_period="UNKNOWN",
    revenue_research_date=RESEARCH_DATE, revenue_evidence="UNKNOWN", revenue_source_url="",
    revenue_note="No revenue figures published or found.",
    **dict(zip(
        ["display_ads","display_ads_evidence","display_ads_source_url","display_ads_note",
         "affiliate","affiliate_evidence","affiliate_source_url","affiliate_note",
         "own_product","own_product_evidence","own_product_source_url","own_product_note",
         "course_or_community","course_or_community_evidence","course_or_community_source_url","course_or_community_note",
         "newsletter_email_capture","newsletter_email_capture_evidence","newsletter_email_capture_source_url","newsletter_email_capture_note"],
        [*bool_field(o,"display_ads"), *bool_field(o,"affiliate"),
         *bool_field(o,"own_product"), *bool_field(o,"course_or_community"), *bool_field(o,"newsletter_email_capture")]
    ))
))

# 8. linkingyourthinking.com
o = base("linkingyourthinking.com")
rows_out.append(dict(
    canonical_root_domain="linkingyourthinking.com", site_name="Linking Your Thinking (Nick Milo)",
    primary_niche=o["primary_niche"],
    sampling_stratum="Narrow Niche Authority",
    traffic_tier=traffic_tier(179900/3), is_niche_authority="Y", is_niche_authority_evidence="D", is_niche_authority_source_url="",
    is_niche_authority_note="LYT is a specific, named PKM sub-methodology distinct from Zettelkasten/PARA, with deep authority inside the Obsidian community.",
    is_contrast_case="N", is_contrast_case_evidence="D", is_contrast_case_source_url="",
    is_contrast_case_note="Not a contrast case; traffic surging per Similarweb at lookup time, consistent with a recently reported book deal.",
    contrast_pattern="NOT_APPLICABLE", contrast_evidence_period="",
    start_year_value="2020", start_year_evidence="B", start_year_source_url="",
    start_year_note="Per Nick Milo's own Medium retrospective, joined Obsidian beta April 2020, shared first 'LYT Kit' May 2020, first formal workshop July 2020.",
    traffic_provider="Similarweb", traffic_metric="total visits", traffic_scope="CONTENT_ONLY",
    traffic_value_raw="179900", traffic_value_raw_period="trailing_3_months",
    traffic_value_monthly_equivalent=str(round(179900/3)), traffic_normalization_method="raw_3mo_total / 3, rounded to nearest integer",
    traffic_research_date=RESEARCH_DATE, traffic_source_period="Similarweb snapshot dated August 2026",
    traffic_evidence="B", traffic_source_url="https://www.similarweb.com/website/linkingyourthinking.com/",
    traffic_note="Global rank #170,471, +34.69% MoM surge -- plausibly related to a recently announced book deal found in search results.",
    revenue_value="UNKNOWN", revenue_figure_period="UNKNOWN",
    revenue_research_date=RESEARCH_DATE, revenue_evidence="UNKNOWN", revenue_source_url="",
    revenue_note="No revenue figures published; workshop/course prices ($129-$4,500) observed are list prices, not revenue.",
    **dict(zip(
        ["display_ads","display_ads_evidence","display_ads_source_url","display_ads_note",
         "affiliate","affiliate_evidence","affiliate_source_url","affiliate_note",
         "own_product","own_product_evidence","own_product_source_url","own_product_note",
         "course_or_community","course_or_community_evidence","course_or_community_source_url","course_or_community_note",
         "newsletter_email_capture","newsletter_email_capture_evidence","newsletter_email_capture_source_url","newsletter_email_capture_note"],
        [*bool_field(o,"display_ads"), *bool_field(o,"affiliate"),
         *bool_field(o,"own_product"), *bool_field(o,"course_or_community"), *bool_field(o,"newsletter_email_capture")]
    ))
))

# 9. 43folders.com
o = base("43folders.com")
rows_out.append(dict(
    canonical_root_domain="43folders.com", site_name="43 Folders (Merlin Mann)",
    primary_niche=o["primary_niche"],
    sampling_stratum="Contrast Cohort",
    traffic_tier=traffic_tier(4000/3), is_niche_authority="Y", is_niche_authority_evidence="D", is_niche_authority_source_url="",
    is_niche_authority_note="Historically one of the original, most influential GTD/lifehacks blogs -- niche authority is a HISTORICAL designation here, independent of its current Contrast Cohort/shutdown status; demonstrates why is_niche_authority and sampling_stratum/is_contrast_case must be separate fields.",
    is_contrast_case="Y", is_contrast_case_evidence="C", is_contrast_case_source_url="https://www.similarweb.com/website/43folders.com/",
    is_contrast_case_note="Directly observed: live domain now 302-redirects to a generic parking page ('This domain has no active website', noindex/nofollow) as of lookup. Independently, a 2008-era MetaFilter thread documents operator Merlin Mann publicly confirming a deliberate, sharp posting-frequency reduction starting ~Sept 2008.",
    contrast_pattern="shutdown", contrast_evidence_period="cadence_drop documented from ~Sept 2008; full domain shutdown/parking directly confirmed as of 2026-09-16 lookup -- presented as reduced-cadence-then-total-shutdown, not a single-moment event.",
    start_year_value="2004", start_year_evidence="B", start_year_source_url="",
    start_year_note="Widely documented (CBS News profile, Wikipedia, GTD forums) as launched by Merlin Mann in 2004/2005, one of the original GTD/lifehacks blogs.",
    traffic_provider="Similarweb", traffic_metric="total visits", traffic_scope="CONTENT_ONLY",
    traffic_value_raw="4000", traffic_value_raw_period="trailing_3_months",
    traffic_value_monthly_equivalent=str(round(4000/3)), traffic_normalization_method="raw_3mo_total / 3, rounded to nearest integer",
    traffic_research_date=RESEARCH_DATE, traffic_source_period="Similarweb snapshot dated August 2026",
    traffic_evidence="B", traffic_source_url="https://www.similarweb.com/website/43folders.com/",
    traffic_note="Global rank #4,105,583, 58.36% MoM decrease -- consistent with a domain no longer actively hosting original content.",
    revenue_value="UNKNOWN", revenue_figure_period="UNKNOWN",
    revenue_research_date=RESEARCH_DATE, revenue_evidence="UNKNOWN", revenue_source_url="",
    revenue_note="No monetization observed since the domain no longer serves original content.",
    **dict(zip(
        ["display_ads","display_ads_evidence","display_ads_source_url","display_ads_note",
         "affiliate","affiliate_evidence","affiliate_source_url","affiliate_note",
         "own_product","own_product_evidence","own_product_source_url","own_product_note",
         "course_or_community","course_or_community_evidence","course_or_community_source_url","course_or_community_note",
         "newsletter_email_capture","newsletter_email_capture_evidence","newsletter_email_capture_source_url","newsletter_email_capture_note"],
        [*bool_field(o,"display_ads", source_url="https://www.43folders.com/"), *bool_field(o,"affiliate", source_url="https://www.43folders.com/"),
         *bool_field(o,"own_product"), *bool_field(o,"course_or_community"), *bool_field(o,"newsletter_email_capture")]
    ))
))

# 10. zenhabits.net
o = base("zenhabits.net")
rows_out.append(dict(
    canonical_root_domain="zenhabits.net", site_name="Zen Habits (Leo Babauta)",
    primary_niche=o["primary_niche"],
    sampling_stratum="Contrast Cohort",
    traffic_tier=traffic_tier(401000/3), is_niche_authority="Y", is_niche_authority_evidence="D", is_niche_authority_source_url="",
    is_niche_authority_note="Time magazine 'Top 25 Blogs' in 2009 and 2010 -- historical niche/culture authority in the productivity-adjacent blogging scene, independent of its current declining-but-active Contrast Cohort status.",
    is_contrast_case="Y", is_contrast_case_evidence="B", is_contrast_case_source_url="https://www.similarweb.com/website/zenhabits.net/",
    is_contrast_case_note="Still active and still monetizing (not fully dead like 43folders.com) -- a milder contrast pattern than 43folders.com's total shutdown.",
    contrast_pattern="traffic_decline", contrast_evidence_period="trailing 3 months ending ~August/September 2026 (Similarweb: global rank worsened #133,150 -> #142,017, -4.89% MoM at most recent reading); contrasted against 2009-2010 Time 'Top 25 Blogs' peak relevance (historically_declined as secondary context, not the quantified metric).",
    start_year_value="2007", start_year_evidence="B", start_year_source_url="",
    start_year_note="Wikipedia's Zen Habits entry states the blog was established February 2007; named to Time's 'Top 25 Blogs' in 2009 and 2010.",
    traffic_provider="Similarweb", traffic_metric="total visits", traffic_scope="CONTENT_ONLY",
    traffic_value_raw="401000", traffic_value_raw_period="trailing_3_months",
    traffic_value_monthly_equivalent=str(round(401000/3)), traffic_normalization_method="raw_3mo_total / 3, rounded to nearest integer",
    traffic_research_date=RESEARCH_DATE, traffic_source_period="Similarweb snapshot dated August 2026",
    traffic_evidence="B", traffic_source_url="https://www.similarweb.com/website/zenhabits.net/",
    traffic_note="Global rank #142,017, -4.89% MoM decrease; global rank itself worsened from #133,150 to #142,017 over the trailing 3 months -- a verified, tool-measured multi-month downward trend, not a single-month blip.",
    revenue_value="UNKNOWN", revenue_figure_period="UNKNOWN",
    revenue_research_date=RESEARCH_DATE, revenue_evidence="UNKNOWN", revenue_source_url="",
    revenue_note="No specific revenue figures published or found; monetization is coaching/courses/books rather than disclosed income reports.",
    **dict(zip(
        ["display_ads","display_ads_evidence","display_ads_source_url","display_ads_note",
         "affiliate","affiliate_evidence","affiliate_source_url","affiliate_note",
         "own_product","own_product_evidence","own_product_source_url","own_product_note",
         "course_or_community","course_or_community_evidence","course_or_community_source_url","course_or_community_note",
         "newsletter_email_capture","newsletter_email_capture_evidence","newsletter_email_capture_source_url","newsletter_email_capture_note"],
        [*bool_field(o,"display_ads"), *bool_field(o,"affiliate"),
         *bool_field(o,"own_product"), *bool_field(o,"course_or_community"), *bool_field(o,"newsletter_email_capture")]
    ))
))

fieldnames = list(rows_out[0].keys())
with open(DST, "w", newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for r in rows_out:
        w.writerow(r)

print(f"Wrote {len(rows_out)} rows, {len(fieldnames)} columns to {DST}")
