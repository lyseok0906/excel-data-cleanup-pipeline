#!/usr/bin/env python3
"""
Migrate validation_10.csv (A0-Phase1 raw research output, informal schema)
into validation_10_v2.csv (Protocol V2 canonical schema).

This script is meant to be re-runnable and reproducible: running it again
against the same validation_10.csv must regenerate a validation_10_v2.csv
that is logically identical (same rows, same columns, same values) to the
one committed in this repo. All fixes that were previously applied as
one-off ad-hoc patches (provenance URL backfills, the traffic_scope-aware
traffic_tier correction for zapier.com) are now baked directly into this
script rather than living only in the final CSV.

No new research is performed here -- every value below is a direct
transcription of facts already gathered and cited during the original
A0-Phase1 research pass and the subsequent targeted provenance repair
(see validation_10_notes.md and research_protocol_v2.md Section 7-A for
the full narrative). This script only reshapes/labels those facts into
the Protocol V2 schema.

Usage:
    python migrate_schema.py [--src PATH] [--dst PATH]

Defaults (no args needed): reads validation_10.csv and writes
validation_10_v2.csv in the same directory as this script's parent
(../validation_10.csv, ../validation_10_v2.csv relative to this file) --
i.e. it works out of the box after a fresh `git clone`, on any OS,
without any environment-specific absolute path.
"""
import argparse
import csv
from pathlib import Path

import domain_utils
import evidence_harden

HERE = Path(__file__).resolve().parent
DEFAULT_SRC = HERE.parent / "validation_10.csv"
DEFAULT_DST = HERE.parent / "validation_10_v2.csv"

RESEARCH_DATE = "2026-09-16"  # ISO. Single lookup session covering all 10 A0-Phase1 rows.

# Traffic tier thresholds (provisional -- see Protocol V2 Section 5-1 and
# Section 12 "미결정 항목" for the note that these need niche-specific
# review before Study A scales to 1000 sites).
TIER_HIGH_MIN = 200_000
TIER_MID_MIN = 20_000


def traffic_tier_for(traffic_scope: str, monthly_equivalent):
    """
    Protocol V2 Section 4-1: traffic_tier depends on traffic_scope, not just
    the raw monthly-equivalent number.
      - WHOLE_DOMAIN_INCLUDES_PRODUCT -> always UNKNOWN (raw value is still
        preserved elsewhere; this function only governs the *tier* label).
      - UNKNOWN scope                 -> always UNKNOWN.
      - CONTENT_ONLY / SUBDIRECTORY_ESTIMATE -> computed from thresholds.
    """
    if traffic_scope in ("WHOLE_DOMAIN_INCLUDES_PRODUCT", "UNKNOWN"):
        return "UNKNOWN"
    if monthly_equivalent is None:
        return "UNKNOWN"
    if monthly_equivalent >= TIER_HIGH_MIN:
        return "HIGH"
    if monthly_equivalent >= TIER_MID_MIN:
        return "MID"
    return "LOW"


# canonical_root_domain -> {field_name: source_url} overrides confirmed during
# the targeted provenance repair pass (research_protocol_v2.md Section 7-A,
# "targeted repair" round). Each URL was re-verified against the SAME
# underlying claim already present in the row's *_note text -- no new claims,
# no new sites. See that section for exactly how each URL was confirmed.
SOURCE_URL_OVERRIDES = {
    "thomasjfrank.com": {
        "start_year_source_url": "https://www.starterstory.com/stories/thomas-frank",
    },
    "zapier.com": {
        "start_year_source_url": "https://zapier.com/blog/erratic-effective-story-behind-zapier-blog-2013/",
    },
    "asianefficiency.com": {
        "start_year_source_url": "https://www.asianefficiency.com/about/",
    },
    "keepproductive.com": {
        "start_year_source_url": "https://theplus.so/who/francesco-dalessio",
    },
    "linkingyourthinking.com": {
        "start_year_source_url": "https://medium.com/@nickmilo22/reflecting-on-the-age-of-the-linked-note-ff13945d6af4",
    },
    "43folders.com": {
        "start_year_source_url": "https://en.wikipedia.org/wiki/Merlin_Mann",
    },
    "zenhabits.net": {
        "start_year_source_url": "https://en.wikipedia.org/wiki/Zen_Habits",
        "display_ads_source_url": "https://zenhabits.net/about/",
    },
}

# Exact, fixed column order -- must match the header of the committed
# validation_10_v2.csv byte-for-byte. Kept as an explicit list (rather than
# "whatever order the dict happened to be built in") so column order is
# deterministic regardless of how the row-building code below evolves.
FIELDNAMES = [
    "canonical_root_domain", "site_name", "primary_niche",
    "sampling_stratum", "traffic_tier",
    "is_niche_authority", "is_niche_authority_evidence", "is_niche_authority_source_url", "is_niche_authority_note",
    "is_contrast_case", "is_contrast_case_evidence", "is_contrast_case_source_url", "is_contrast_case_note",
    "contrast_pattern", "contrast_evidence_period",
    "start_year_value", "start_year_evidence", "start_year_source_url", "start_year_note",
    "traffic_provider", "traffic_metric", "traffic_scope",
    "traffic_value_raw", "traffic_value_raw_period", "traffic_value_monthly_equivalent",
    "traffic_normalization_method", "traffic_research_date", "traffic_source_period",
    "traffic_evidence", "traffic_source_url", "traffic_note",
    "revenue_value", "revenue_figure_period", "revenue_research_date",
    "revenue_evidence", "revenue_source_url", "revenue_note",
    "display_ads", "display_ads_evidence", "display_ads_source_url", "display_ads_note",
    "affiliate", "affiliate_evidence", "affiliate_source_url", "affiliate_note",
    "own_product", "own_product_evidence", "own_product_source_url", "own_product_note",
    "course_or_community", "course_or_community_evidence", "course_or_community_source_url", "course_or_community_note",
    "newsletter_email_capture", "newsletter_email_capture_evidence", "newsletter_email_capture_source_url", "newsletter_email_capture_note",
]

BOOL_FIELDS_WITH_SOURCE = [
    "display_ads", "affiliate", "own_product", "course_or_community", "newsletter_email_capture",
]


def load_source(src_path: Path):
    with src_path.open(newline="", encoding="utf-8") as f:
        return {r["canonical_root_domain"]: r for r in csv.DictReader(f)}


def bool_field(o, field, source_url="", note_extra=""):
    """
    Migrate one boolean field (value/evidence/note in the old schema) into
    the new value/evidence/source_url/note quadruple, enforcing Rule #8:
    an UNKNOWN value must always carry UNKNOWN evidence (never a D-level
    inference left dangling on an UNKNOWN value).
    """
    v = o[field].strip()
    ev = o[field + "_evidence"].strip()
    note = o[field + "_note"].strip()
    if v == "UNKNOWN":
        ev = "UNKNOWN"
    if note_extra:
        note = (note + " " + note_extra).strip()
    return v, ev, source_url, note


def round_monthly(raw_value_str, period_months=3):
    try:
        raw = float(raw_value_str)
    except (TypeError, ValueError):
        return None
    return round(raw / period_months)


def build_rows(old: dict) -> list:
    rows = []

    def row(canonical_root_domain, site_name, primary_niche, sampling_stratum,
             is_niche_authority, is_niche_authority_note,
             is_contrast_case, is_contrast_case_evidence, is_contrast_case_source_url, is_contrast_case_note,
             contrast_pattern, contrast_evidence_period,
             start_year_value, start_year_evidence, start_year_note,
             traffic_provider, traffic_metric, traffic_scope,
             traffic_value_raw, traffic_value_raw_period, traffic_source_period, traffic_evidence,
             traffic_source_url, traffic_note,
             revenue_value, revenue_figure_period, revenue_evidence, revenue_source_url, revenue_note,
             bool_values):
        monthly = round_monthly(traffic_value_raw) if traffic_value_raw not in ("UNKNOWN", None, "") else None
        tier = traffic_tier_for(traffic_scope, monthly)
        overrides = SOURCE_URL_OVERRIDES.get(canonical_root_domain, {})

        d = {
            "canonical_root_domain": canonical_root_domain,
            "site_name": site_name,
            "primary_niche": primary_niche,
            "sampling_stratum": sampling_stratum,
            "traffic_tier": tier,
            "is_niche_authority": is_niche_authority,
            "is_niche_authority_evidence": "D",
            "is_niche_authority_source_url": "",
            "is_niche_authority_note": is_niche_authority_note,
            "is_contrast_case": is_contrast_case,
            "is_contrast_case_evidence": is_contrast_case_evidence,
            "is_contrast_case_source_url": is_contrast_case_source_url,
            "is_contrast_case_note": is_contrast_case_note,
            "contrast_pattern": contrast_pattern,
            "contrast_evidence_period": contrast_evidence_period,
            "start_year_value": start_year_value,
            "start_year_evidence": start_year_evidence,
            "start_year_source_url": overrides.get("start_year_source_url", ""),
            "start_year_note": start_year_note,
            "traffic_provider": traffic_provider,
            "traffic_metric": traffic_metric,
            "traffic_scope": traffic_scope,
            "traffic_value_raw": traffic_value_raw,
            "traffic_value_raw_period": traffic_value_raw_period,
            "traffic_value_monthly_equivalent": ("UNKNOWN" if monthly is None else str(monthly)),
            "traffic_normalization_method": (
                "UNKNOWN" if monthly is None else "raw_3mo_total / 3, rounded to nearest integer"
            ),
            "traffic_research_date": RESEARCH_DATE,
            "traffic_source_period": traffic_source_period,
            "traffic_evidence": traffic_evidence,
            "traffic_source_url": traffic_source_url,
            "traffic_note": traffic_note,
            "revenue_value": revenue_value,
            "revenue_figure_period": revenue_figure_period,
            "revenue_research_date": RESEARCH_DATE,
            "revenue_evidence": revenue_evidence,
            "revenue_source_url": revenue_source_url,
            "revenue_note": revenue_note,
        }
        for field in BOOL_FIELDS_WITH_SOURCE:
            v, ev, url, note = bool_values[field]
            url = overrides.get(field + "_source_url", url)
            d[field] = v
            d[field + "_evidence"] = ev
            d[field + "_source_url"] = url
            d[field + "_note"] = note
        rows.append(evidence_harden.harden_row(d))

    # ---- 1. thomasjfrank.com ----
    o = old["thomasjfrank.com"]
    row(
        "thomasjfrank.com", "Thomas Frank", o["primary_niche"], "Large/Traffic Leader",
        "N", "Large personal-brand/creator site; not the singular reference site for a named sub-methodology the way fortelabs.com/zettelkasten.de/linkingyourthinking.com are.",
        "N", "D", "", "Not a contrast case; used as Large/Traffic Leader example. The -25.66% MoM dip Similarweb reported is a single-month snapshot, not a verified multi-period decline.",
        "NOT_APPLICABLE", "",
        "2010", "B", "Started as 'College Info Geek' blog in 2010; pivoted the business around Notion templates starting 2021, per Starter Story interview.",
        "Similarweb", "total visits", "CONTENT_ONLY",
        "118600", "trailing_3_months", "Similarweb snapshot dated August 2026", "B",
        "https://www.similarweb.com/website/thomasjfrank.com/",
        "Global rank #345,634 at lookup; 25.66% MoM decline observed at time of lookup (single-month reading). Similarweb free-tier estimates are directional only.",
        "UNKNOWN", "2021-2023 (cumulative), recent monthly figure as of 2023 interview",
        "UNKNOWN", "UNKNOWN",
        "[pre-950 hardening] revenue_value normalized to UNKNOWN per the Study A revenue-field policy: Study A does not treat compound/fragmentary self-reported figures spanning multiple periods as a single structured revenue_value. The original figures are preserved here for context only, not as a structured value: self-reported by Thomas Frank in a Starter Story interview (https://www.starterstory.com/stories/thomas-frank) -- ~$120K/mo template sales + ~$15K/mo affiliate/AdSense + $1,200/mo Pipedream affiliate, plus a separate cumulative claim of ~$2.1M over 2021-2023 from templates and a 'recent' ~$175,000/month figure. These would have been A-tier (operator's own words, via a third-party interview) if Study A used a structured revenue field, but per the current policy any Study-B-style deep revenue reconstruction is out of scope for Study A.",
        {
            "display_ads": bool_field(o, "display_ads"),
            "affiliate": bool_field(o, "affiliate", source_url="https://www.starterstory.com/stories/thomas-frank"),
            "own_product": bool_field(o, "own_product"),
            "course_or_community": bool_field(o, "course_or_community"),
            "newsletter_email_capture": bool_field(o, "newsletter_email_capture"),
        },
    )

    # ---- 2. zapier.com ----
    o = old["zapier.com"]
    row(
        "zapier.com", "Zapier Blog", o["primary_niche"], "Large/Traffic Leader",
        "N", "Company content-marketing blog, not a singular named-methodology authority site.",
        "N", "D", "", "Not a contrast case; included as Large/Traffic Leader example, flagged as a company-blog edge case (see traffic_scope).",
        "NOT_APPLICABLE", "",
        "2012", "B", "Zapier itself was founded in 2011 (Y Combinator); the blog's content-marketing engine is widely dated to ~2012-2013 per third-party retrospectives.",
        "Similarweb", "total visits", "WHOLE_DOMAIN_INCLUDES_PRODUCT",
        "5300000", "trailing_3_months", "Similarweb snapshot dated August 2026", "B",
        "https://www.similarweb.com/website/zapier.com/",
        "Figure is for the ENTIRE zapier.com domain (app + marketing site + blog combined), not blog traffic alone -- see traffic_scope=WHOLE_DOMAIN_INCLUDES_PRODUCT. Not comparable to CONTENT_ONLY rows in this dataset without adjustment. [schema patch] traffic_scope=WHOLE_DOMAIN_INCLUDES_PRODUCT, so content-level traffic_tier is forced to UNKNOWN per protocol rule, even though raw traffic_value_raw/monthly_equivalent (whole-domain figures) are preserved unchanged. Previously mis-derived tier was HIGH computed from whole-domain traffic, which is not valid for a content-only tier.",
        "UNKNOWN", "UNKNOWN",
        "UNKNOWN", "",
        "Blog-attributable revenue not separable from overall SaaS company revenue. Zapier is reported elsewhere as a large, profitable SaaS company, but no source attributes a figure to blog content specifically.",
        {
            "display_ads": bool_field(o, "display_ads"),
            "affiliate": bool_field(o, "affiliate"),
            "own_product": bool_field(o, "own_product"),
            "course_or_community": bool_field(o, "course_or_community"),
            "newsletter_email_capture": bool_field(o, "newsletter_email_capture"),
        },
    )

    # ---- 3. asianefficiency.com ----
    o = old["asianefficiency.com"]
    row(
        "asianefficiency.com", "Asian Efficiency", o["primary_niche"], "Large/Traffic Leader",
        "N", "Broad time-management/productivity coaching brand, not the singular reference site for one named sub-methodology.",
        "N", "D", "https://www.similarweb.com/website/asianefficiency.com/",
        "Not formally flagged as contrast case in this pass, though measured traffic (~11.9K/mo, LOW tier) and a 19.37% MoM dip are notably weaker than its 14-year operating history and press mentions would suggest -- borderline; flagged for reconsideration alongside is_niche_authority/traffic_tier separation (sampling_stratum=Large/Traffic Leader but traffic_tier=LOW is exactly the kind of stratum/tier mismatch this schema field split is meant to surface).",
        "NOT_APPLICABLE", "",
        "2011", "B", "About page describes the blog/newsletter starting as a passion project in 2011 (founder Thanh Pham's personal productivity journey began 2008).",
        "Similarweb", "total visits", "CONTENT_ONLY",
        "35700", "trailing_3_months", "Similarweb snapshot dated August 2026", "B",
        "https://www.similarweb.com/website/asianefficiency.com/",
        "Global rank #889,548, 19.37% MoM decrease at time of lookup.",
        "UNKNOWN", "UNKNOWN",
        "UNKNOWN", "",
        "No self-published income figures found; site reports 50,000+ newsletter subscribers as an audience-size proxy, not a revenue figure.",
        {
            "display_ads": bool_field(o, "display_ads"),
            "affiliate": bool_field(
                o, "affiliate",
                note_extra="[schema patch] evidence downgraded from D to UNKNOWN per Rule #8 (UNKNOWN value must carry UNKNOWN evidence); the D-level inference reasoning is preserved here as context only, not as evidence backing.",
            ),
            "own_product": bool_field(o, "own_product"),
            "course_or_community": bool_field(o, "course_or_community"),
            "newsletter_email_capture": bool_field(o, "newsletter_email_capture"),
        },
    )
    # Rule #8 enforcement for a case where the source note itself argued for D:
    rows[-1]["affiliate_evidence"] = "UNKNOWN"

    # ---- 4. nesslabs.com ----
    o = old["nesslabs.com"]
    row(
        "nesslabs.com", "Ness Labs", o["primary_niche"], "Mid-scale Active Site",
        "N", "Newsletter-first creator brand covering mindful productivity broadly, not a singular named-methodology reference site.",
        "N", "D", "", "Not a contrast case; active and growing per Similarweb's positive MoM trend at lookup time.",
        "NOT_APPLICABLE", "",
        "2018", "D", "Exact founding date not confirmed on-site; multiple secondary creator-story profiles place launch around 2018. Inference, not first-party statement.",
        "Similarweb", "total visits", "CONTENT_ONLY",
        "269100", "trailing_3_months", "Similarweb snapshot dated June 2026", "B",
        "https://www.similarweb.com/website/nesslabs.com/",
        "Global rank #172,591, +15.87% MoM increase at time of lookup.",
        "UNKNOWN", "UNKNOWN",
        "UNKNOWN", "",
        "No self-published revenue figures found on-site; third-party creator-economy interviews discuss growth strategy but not exact revenue.",
        {
            "display_ads": bool_field(o, "display_ads"),
            "affiliate": bool_field(o, "affiliate"),
            "own_product": bool_field(o, "own_product"),
            "course_or_community": bool_field(o, "course_or_community"),
            "newsletter_email_capture": bool_field(o, "newsletter_email_capture"),
        },
    )

    # ---- 5. keepproductive.com ----
    o = old["keepproductive.com"]
    row(
        "keepproductive.com", "Keep Productive", o["primary_niche"], "Mid-scale Active Site",
        "N", "Notion/productivity app review creator, not a singular named-methodology reference site.",
        "N", "D", "", "Not treated as contrast case; content/YouTube channel appear ongoing per search hits, but this is an inference given incomplete direct access (robots.txt blocked).",
        "NOT_APPLICABLE", "",
        "2017", "A", "Founder Francesco D'Alessio quoted directly: 'We started Keep Productive in late 2017, after 3 previous years on YouTube.'",
        "Similarweb", "total visits", "CONTENT_ONLY",
        "UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN",
        "https://www.similarweb.com/website/keepproductive.com/",
        "Similarweb free overview returned 'No Data to Display'; robots.txt also blocked direct site fetch. Genuinely unknown from available tools -- left UNKNOWN per schema rules rather than guessed. [pre-950 hardening] traffic_scope reclassified from UNKNOWN to CONTENT_ONLY: this is a domain-structure judgment (keepproductive.com is a Notion/productivity review + YouTube-linked creator site, not a SaaS/app domain), independent of the fact that no traffic NUMBER could be obtained -- Section 3-6 traffic_scope and the traffic value itself are separate axes.",
        "UNKNOWN", "UNKNOWN",
        "UNKNOWN", "",
        "No self-published revenue figures found.",
        {
            "display_ads": bool_field(o, "display_ads"),
            "affiliate": bool_field(o, "affiliate", source_url="https://theplus.so/who/francesco-dalessio"),
            "own_product": bool_field(o, "own_product", source_url="https://theplus.so/who/francesco-dalessio"),
            "course_or_community": bool_field(o, "course_or_community", source_url="https://theplus.so/who/francesco-dalessio"),
            "newsletter_email_capture": bool_field(o, "newsletter_email_capture"),
        },
    )

    # ---- 6. fortelabs.com ----
    o = old["fortelabs.com"]
    row(
        "fortelabs.com", "Forte Labs (Building a Second Brain / Tiago Forte)", o["primary_niche"], "Narrow Niche Authority",
        "Y", "Originating source of the PARA Method / 'Building a Second Brain' framework specifically; globally recognized book/course franchise within the PKM sub-niche.",
        "N", "D", "", "Not a contrast case; traffic trending up per Similarweb at lookup time.",
        "NOT_APPLICABLE", "",
        "2015", "D", "Exact founding year not stated on fetched pages; inference from surrounding post dates and community history, not a first-party statement.",
        "Similarweb", "total visits", "CONTENT_ONLY",
        "281000", "trailing_3_months", "Similarweb snapshot dated July 2026", "B",
        "https://www.similarweb.com/website/fortelabs.com/",
        "Global rank #169,158, +5.19% MoM growth at time of lookup -- comparable to or higher than some Large-tier sites, illustrating traffic_tier and sampling_stratum need not align.",
        "UNKNOWN", "UNKNOWN",
        "UNKNOWN", "",
        "No specific revenue figures found; a 2024 retrospective post references undisclosed 'sales milestones' for the book without numbers.",
        {
            "display_ads": bool_field(o, "display_ads"),
            "affiliate": bool_field(
                o, "affiliate",
                note_extra="[schema patch] evidence downgraded from D to UNKNOWN per Rule #8; original D-level inference (plausible affiliate links in 'best apps' content, not directly disclosed) preserved as context only.",
            ),
            "own_product": bool_field(o, "own_product"),
            "course_or_community": bool_field(o, "course_or_community"),
            "newsletter_email_capture": bool_field(o, "newsletter_email_capture"),
        },
    )
    rows[-1]["affiliate_evidence"] = "UNKNOWN"

    # ---- 7. zettelkasten.de ----
    o = old["zettelkasten.de"]
    row(
        "zettelkasten.de", "Zettelkasten Method (zettelkasten.de)", o["primary_niche"], "Narrow Niche Authority",
        "Y", "Definitive, long-running reference site for the specific Zettelkasten method, run by co-authors of the reference book on the topic.",
        "N", "D", "", "Not a contrast case; growing traffic per Similarweb at lookup time.",
        "NOT_APPLICABLE", "",
        "2013", "D", "Exact launch date not stated on fetched pages; inferred from surrounding post dates and community history (Sascha Fast's biography post dated Dec 2014).",
        "Similarweb", "total visits", "CONTENT_ONLY",
        "105500", "trailing_3_months", "Similarweb snapshot dated June 2026", "B",
        "https://www.similarweb.com/website/zettelkasten.de/",
        "Global rank #395,998, +11.58% MoM growth; notably high 3m24s average visit duration suggesting an engaged niche readership.",
        "UNKNOWN", "UNKNOWN",
        "UNKNOWN", "",
        "No revenue figures published or found.",
        {
            "display_ads": bool_field(o, "display_ads"),
            "affiliate": bool_field(o, "affiliate"),
            "own_product": bool_field(o, "own_product"),
            "course_or_community": bool_field(o, "course_or_community"),
            "newsletter_email_capture": bool_field(o, "newsletter_email_capture"),
        },
    )

    # ---- 8. linkingyourthinking.com ----
    o = old["linkingyourthinking.com"]
    row(
        "linkingyourthinking.com", "Linking Your Thinking (Nick Milo)", o["primary_niche"], "Narrow Niche Authority",
        "Y", "LYT is a specific, named PKM sub-methodology distinct from Zettelkasten/PARA, with deep authority inside the Obsidian community.",
        "N", "D", "", "Not a contrast case; traffic surging per Similarweb at lookup time, consistent with a recently reported book deal.",
        "NOT_APPLICABLE", "",
        "2020", "B", "Per Nick Milo's own Medium retrospective, joined Obsidian beta April 2020, shared first 'LYT Kit' May 2020, first formal workshop July 2020.",
        "Similarweb", "total visits", "CONTENT_ONLY",
        "179900", "trailing_3_months", "Similarweb snapshot dated August 2026", "B",
        "https://www.similarweb.com/website/linkingyourthinking.com/",
        "Global rank #170,471, +34.69% MoM surge -- plausibly related to a recently announced book deal found in search results.",
        "UNKNOWN", "UNKNOWN",
        "UNKNOWN", "",
        "No revenue figures published; workshop/course prices ($129-$4,500) observed are list prices, not revenue.",
        {
            "display_ads": bool_field(o, "display_ads"),
            "affiliate": bool_field(o, "affiliate"),
            "own_product": bool_field(o, "own_product"),
            "course_or_community": bool_field(o, "course_or_community"),
            "newsletter_email_capture": bool_field(o, "newsletter_email_capture"),
        },
    )

    # ---- 9. 43folders.com ----
    o = old["43folders.com"]
    row(
        "43folders.com", "43 Folders (Merlin Mann)", o["primary_niche"], "Contrast Cohort",
        "Y", "Historically one of the original, most influential GTD/lifehacks blogs -- niche authority is a HISTORICAL designation here, independent of its current Contrast Cohort/shutdown status; demonstrates why is_niche_authority and sampling_stratum/is_contrast_case must be separate fields.",
        "Y", "C", "https://www.similarweb.com/website/43folders.com/",
        "Directly observed: live domain now 302-redirects to a generic parking page ('This domain has no active website', noindex/nofollow) as of lookup. Independently, a 2008-era MetaFilter thread documents operator Merlin Mann publicly confirming a deliberate, sharp posting-frequency reduction starting ~Sept 2008.",
        "shutdown",
        "cadence_drop documented from ~Sept 2008; full domain shutdown/parking directly confirmed as of 2026-09-16 lookup -- presented as reduced-cadence-then-total-shutdown, not a single-moment event.",
        "2004", "B", "Widely documented (CBS News profile, Wikipedia, GTD forums) as launched by Merlin Mann in 2004/2005, one of the original GTD/lifehacks blogs.",
        "Similarweb", "total visits", "CONTENT_ONLY",
        "4000", "trailing_3_months", "Similarweb snapshot dated August 2026", "B",
        "https://www.similarweb.com/website/43folders.com/",
        "Global rank #4,105,583, 58.36% MoM decrease -- consistent with a domain no longer actively hosting original content.",
        "UNKNOWN", "UNKNOWN",
        "UNKNOWN", "",
        "No monetization observed since the domain no longer serves original content.",
        {
            "display_ads": bool_field(o, "display_ads", source_url="https://www.43folders.com/"),
            "affiliate": bool_field(o, "affiliate", source_url="https://www.43folders.com/"),
            "own_product": bool_field(o, "own_product"),
            "course_or_community": bool_field(o, "course_or_community"),
            "newsletter_email_capture": bool_field(o, "newsletter_email_capture"),
        },
    )

    # ---- 10. zenhabits.net ----
    o = old["zenhabits.net"]
    row(
        "zenhabits.net", "Zen Habits (Leo Babauta)", o["primary_niche"], "Contrast Cohort",
        "Y", "Time magazine 'Top 25 Blogs' in 2009 and 2010 -- historical niche/culture authority in the productivity-adjacent blogging scene, independent of its current declining-but-active Contrast Cohort status.",
        "Y", "B", "https://www.similarweb.com/website/zenhabits.net/",
        "Still active and still monetizing (not fully dead like 43folders.com) -- a milder contrast pattern than 43folders.com's total shutdown.",
        "traffic_decline",
        "trailing 3 months ending ~August/September 2026 (Similarweb: global rank worsened #133,150 -> #142,017, -4.89% MoM at most recent reading); contrasted against 2009-2010 Time 'Top 25 Blogs' peak relevance (historically_declined as secondary context, not the quantified metric).",
        "2007", "B", "Wikipedia's Zen Habits entry states the blog was established February 2007; named to Time's 'Top 25 Blogs' in 2009 and 2010.",
        "Similarweb", "total visits", "CONTENT_ONLY",
        "401000", "trailing_3_months", "Similarweb snapshot dated August 2026", "B",
        "https://www.similarweb.com/website/zenhabits.net/",
        "Global rank #142,017, -4.89% MoM decrease; global rank itself worsened from #133,150 to #142,017 over the trailing 3 months -- a verified, tool-measured multi-month downward trend, not a single-month blip.",
        "UNKNOWN", "UNKNOWN",
        "UNKNOWN", "",
        "No specific revenue figures published or found; monetization is coaching/courses/books rather than disclosed income reports.",
        {
            "display_ads": bool_field(o, "display_ads"),
            "affiliate": bool_field(o, "affiliate"),
            "own_product": bool_field(o, "own_product"),
            "course_or_community": bool_field(o, "course_or_community"),
            "newsletter_email_capture": bool_field(o, "newsletter_email_capture"),
        },
    )

    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--src", type=Path, default=DEFAULT_SRC, help="Path to validation_10.csv (default: ../validation_10.csv relative to this script)")
    parser.add_argument("--dst", type=Path, default=DEFAULT_DST, help="Path to write validation_10_v2.csv (default: ../validation_10_v2.csv relative to this script)")
    args = parser.parse_args()

    old = load_source(args.src)
    rows = build_rows(old)

    # Sanity check: every domain in the source file was migrated, in a fixed order.
    expected_order = [
        "thomasjfrank.com", "zapier.com", "asianefficiency.com", "nesslabs.com",
        "keepproductive.com", "fortelabs.com", "zettelkasten.de",
        "linkingyourthinking.com", "43folders.com", "zenhabits.net",
    ]
    got_order = [r["canonical_root_domain"] for r in rows]
    if got_order != expected_order:
        raise SystemExit(f"Row order drift detected: expected {expected_order}, got {got_order}")

    with args.dst.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        for r in rows:
            missing = set(FIELDNAMES) - set(r.keys())
            extra = set(r.keys()) - set(FIELDNAMES)
            if missing or extra:
                raise SystemExit(f"Column mismatch for {r['canonical_root_domain']}: missing={missing} extra={extra}")
            w.writerow({k: r[k] for k in FIELDNAMES})

    print(f"Wrote {len(rows)} rows, {len(FIELDNAMES)} columns to {args.dst}")


if __name__ == "__main__":
    main()
