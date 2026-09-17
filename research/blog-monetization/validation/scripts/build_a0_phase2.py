#!/usr/bin/env python3
"""
A0-Phase2: builds the 40 new-site rows (Excel/Spreadsheet x10, Personal
Finance x10, Home/DIY & Food x10, Product Review/Buying Guides x10) directly
in the Protocol V2 canonical schema, then concatenates them with the existing
10-site validation_10_v2.csv into a cumulative 50-site dataset.

This script does NOT do any web research itself -- all facts here were
gathered by dedicated research passes (WebSearch/WebFetch) immediately
before this script was written, and are transcribed here verbatim with
their evidence tiers and source URLs. No number or URL in this file was
invented by this script.

Usage:
    python build_a0_phase2.py
Writes (relative to this script's parent directory, i.e. validation/):
    a0_phase2_40.csv       -- the 40 new sites only
    validation_50_v2.csv   -- 10 (A0-Phase1) + 40 (A0-Phase2) = 50 rows
"""
import csv
from pathlib import Path

import migrate_schema  # reuse FIELDNAMES + traffic_tier_for + round_monthly
import evidence_harden
import schema_extend

HERE = Path(__file__).resolve().parent
OUT_40 = HERE.parent / "a0_phase2_40.csv"
OUT_50 = HERE.parent / "validation_50_v2.csv"
EXISTING_10 = HERE.parent / "validation_10_v2.csv"

FIELDNAMES = migrate_schema.FIELDNAMES
RESEARCH_DATE = "2026-09-17"

UNKNOWN = "UNKNOWN"


def bf(value, evidence=UNKNOWN, url=UNKNOWN, note=""):
    """Boolean/enum field 4-tuple with Rule #8 enforced (UNKNOWN value -> UNKNOWN evidence)."""
    value = value.strip()
    if value == UNKNOWN:
        evidence = UNKNOWN
    return value, evidence, url, note


def traffic_block(provider, metric, scope, raw, raw_period, monthly, norm_method,
                   source_period, evidence, url, note, research_date=RESEARCH_DATE):
    return dict(
        traffic_provider=provider,
        traffic_metric=metric,
        traffic_scope=scope,
        traffic_value_raw=raw,
        traffic_value_raw_period=raw_period,
        traffic_value_monthly_equivalent=monthly,
        traffic_normalization_method=norm_method,
        traffic_research_date=research_date,
        traffic_source_period=source_period,
        traffic_evidence=evidence if raw != UNKNOWN else UNKNOWN,
        traffic_source_url=url,
        traffic_note=note,
    )


def row(canonical_root_domain, site_name, primary_niche, sampling_stratum,
        is_niche_authority, is_niche_authority_note="", is_niche_authority_evidence=UNKNOWN, is_niche_authority_url=UNKNOWN,
        is_contrast_case="N", is_contrast_case_evidence="D", is_contrast_case_url=UNKNOWN,
        is_contrast_case_note="No verified contrast-pattern evidence (traffic decline, cadence drop, shutdown, etc.) was found for this site during this research pass; defaulted to N.",
        contrast_pattern="NOT_APPLICABLE", contrast_evidence_period="",
        start_year="UNKNOWN", start_year_evidence=UNKNOWN, start_year_url=UNKNOWN, start_year_note="",
        traffic=None,
        revenue_value="UNKNOWN", revenue_figure_period="", revenue_evidence=UNKNOWN, revenue_url=UNKNOWN, revenue_note="",
        display_ads=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
        affiliate=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
        own_product=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
        course_or_community=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
        newsletter_email_capture=("UNKNOWN", UNKNOWN, UNKNOWN, "")):

    d = {
        "canonical_root_domain": canonical_root_domain,
        "site_name": site_name,
        "primary_niche": primary_niche,
        "sampling_stratum": sampling_stratum,
    }

    v, e, u, n = bf(is_niche_authority, is_niche_authority_evidence, is_niche_authority_url, is_niche_authority_note)
    d["is_niche_authority"], d["is_niche_authority_evidence"], d["is_niche_authority_source_url"], d["is_niche_authority_note"] = v, e, u, n

    v, e, u, n = bf(is_contrast_case, is_contrast_case_evidence, is_contrast_case_url, is_contrast_case_note)
    d["is_contrast_case"], d["is_contrast_case_evidence"], d["is_contrast_case_source_url"], d["is_contrast_case_note"] = v, e, u, n

    d["contrast_pattern"] = contrast_pattern
    d["contrast_evidence_period"] = contrast_evidence_period

    sy_evidence = UNKNOWN if start_year == UNKNOWN else start_year_evidence
    d["start_year_value"] = start_year
    d["start_year_evidence"] = sy_evidence
    d["start_year_source_url"] = start_year_url if start_year != UNKNOWN else UNKNOWN
    d["start_year_note"] = start_year_note

    if traffic is None:
        traffic = traffic_block(UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN, "", UNKNOWN, "", "", UNKNOWN, UNKNOWN, "")
    d.update(traffic)

    monthly = traffic["traffic_value_monthly_equivalent"]
    monthly_num = None
    if isinstance(monthly, (int, float)):
        monthly_num = monthly
    d["traffic_tier"] = migrate_schema.traffic_tier_for(traffic["traffic_scope"], monthly_num)

    rev_evidence = UNKNOWN if revenue_value == UNKNOWN else revenue_evidence
    d["revenue_value"] = revenue_value
    d["revenue_figure_period"] = revenue_figure_period
    d["revenue_research_date"] = RESEARCH_DATE if revenue_value != UNKNOWN or revenue_evidence != UNKNOWN else RESEARCH_DATE
    d["revenue_evidence"] = rev_evidence
    d["revenue_source_url"] = revenue_url if revenue_value != UNKNOWN else UNKNOWN
    d["revenue_note"] = revenue_note

    for field, spec in [
        ("display_ads", display_ads),
        ("affiliate", affiliate),
        ("own_product", own_product),
        ("course_or_community", course_or_community),
        ("newsletter_email_capture", newsletter_email_capture),
    ]:
        v, e, u, n = bf(*spec)
        d[field] = v
        d[field + "_evidence"] = e
        d[field + "_source_url"] = u
        d[field + "_note"] = n

    # Production-schema fields (category/sub_category/as_of_date/content_scale_proxy_*)
    # are added in bulk after all 40 rows are built (schema_extend.extend_rows_with_production_schema),
    # so they are expected to be "missing" at this per-row construction stage.
    missing = set(FIELDNAMES) - set(d.keys()) - set(schema_extend.ALL_NEW_FIELDNAMES)
    extra = set(d.keys()) - set(FIELDNAMES)
    if missing or extra:
        raise SystemExit(f"Column mismatch for {canonical_root_domain}: missing={missing} extra={extra}")
    return d


rows = []

# ============================================================
# CATEGORY 1: Excel / Spreadsheet & Data Tools (10 sites)
# ============================================================

rows.append(row(
    "mrexcel.com", "MrExcel Publishing / MrExcel Message Board",
    "Excel Q&A forum, tips, and books (Bill Jelen / \"Mr. Excel\")",
    "Large/Traffic Leader",
    is_niche_authority="Y", is_niche_authority_evidence="B", is_niche_authority_url="https://www.mrexcel.com/meet-mrexcel/",
    is_niche_authority_note="One of the oldest, most-cited Excel help forums; founder Bill Jelen widely known as \"Mr. Excel\".",
    is_contrast_case="N", is_contrast_case_evidence="D", is_contrast_case_note="No decline evidence found; treated as active Large/Traffic Leader.",
    start_year="1998", start_year_evidence="A", start_year_url="https://www.mrexcel.com/",
    start_year_note="Own site tagline: \"Excel Tips & Solutions Since 1998\".",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", 441700, "trailing_3_months", round(441700/3),
        "raw_3mo_total / 3, rounded to nearest integer", "Similarweb snapshot dated August 2026", "B",
        "https://www.similarweb.com/website/mrexcel.com/",
        "Traffic decreased 7.41% vs last month at time of lookup.",
    ),
    display_ads=("Y", "C", "https://www.mrexcel.com/", "Merch/product banners and \"Featured Products\" observed on homepage."),
    affiliate=("UNKNOWN", UNKNOWN, UNKNOWN, "Not verified this pass."),
    own_product=("Y", "C", "https://www.mrexcel.com/", "Sells Bill Jelen's own books and the paid \"MrExcel Library\" knowledge base."),
    course_or_community=("Y", "C", "https://www.mrexcel.com/", "Paid \"MrExcel Library\" (webinars/training) plus free forum community."),
    newsletter_email_capture=("UNKNOWN", UNKNOWN, UNKNOWN, "Not observed in fetched excerpt."),
))

rows.append(row(
    "excelforum.com", "Excel Forum",
    "Excel/VBA community Q&A forum",
    "Large/Traffic Leader",
    is_niche_authority="Y", is_niche_authority_evidence="D",
    is_niche_authority_note="Long-standing large general Excel help forum; inference from stated scale of traffic/signups, not a third-party ranking source.",
    is_contrast_case="N", is_contrast_case_evidence="D", is_contrast_case_note="No decline evidence found.",
    start_year=UNKNOWN, start_year_note="Own \"About Excel Forum\" page gives current stats only, no founding date found.",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", 231900, "trailing_3_months", round(231900/3),
        "raw_3mo_total / 3, rounded to nearest integer", "Similarweb snapshot dated August 2026", "B",
        "https://www.similarweb.com/website/excelforum.com/",
        "Traffic decreased 12.97% vs last month. Note: the site's own about page separately claims "
        "\"~1500 signups and 1.5 million monthly visitors\" (https://www.excelforum.com/excel-new-users-basics/1166819-about-excel-forum.html, tier A, no period stated) "
        "which disagrees with Similarweb by roughly an order of magnitude -- flagged as a genuine discrepancy between self-reported and third-party-tool traffic, not resolved by picking one.",
    ),
    display_ads=("UNKNOWN", UNKNOWN, UNKNOWN, "Not directly observed this pass."),
    affiliate=("UNKNOWN", UNKNOWN, UNKNOWN, "Not directly observed this pass."),
    own_product=("N", "D", UNKNOWN, "Appears to be a pure community forum; no evidence of an own product found."),
    course_or_community=("Y", "C", "https://www.excelforum.com/", "The forum itself is the community/product."),
    newsletter_email_capture=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
))

rows.append(row(
    "excel-easy.com", "Excel Easy",
    "Free Excel tutorial site (beginner-to-intermediate)",
    "Mid-scale Active Site",
    is_niche_authority="N", is_niche_authority_evidence="D",
    is_niche_authority_note="General beginner tutorial site, not tied to one specific named sub-methodology.",
    is_contrast_case="N", is_contrast_case_evidence="D",
    start_year="2010", start_year_evidence="B", start_year_url="https://spreadsheeto.com/best-excel-blogs/",
    start_year_note="Launched by students at the University of Amsterdam per a third-party profile of founder Niels Weterings.",
    traffic=traffic_block(
        "Similarweb", "total visits (label ambiguous)", "CONTENT_ONLY", 291500, UNKNOWN, UNKNOWN,
        "Similarweb page did not clearly confirm whether 291.5K was a 3-month total or another metric; left un-normalized rather than guessing the period.",
        "Similarweb snapshot dated June 2026", "B",
        "https://www.similarweb.com/website/excel-easy.com/",
        "Site itself separately states \"Join more than 1 million monthly learners\" (tier A, no period specified, https://www.excel-easy.com/) -- not reconciled with the Similarweb figure.",
    ),
    display_ads=("N", "D", UNKNOWN, "None observed in a partial fetched excerpt; not an exhaustive audit."),
    affiliate=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    own_product=("UNKNOWN", UNKNOWN, UNKNOWN, "No product/course found in fetched excerpt."),
    course_or_community=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    newsletter_email_capture=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
))

rows.append(row(
    "automateexcel.com", "Automate Excel",
    "VBA/macro automation tutorials, formula guides, own add-in products",
    "Mid-scale Active Site",
    is_niche_authority="N", is_niche_authority_evidence="D",
    is_niche_authority_note="Broad VBA/formula tutorial site plus tool vendor, not a single-topic authority.",
    is_contrast_case="N", is_contrast_case_evidence="D",
    start_year="2004", start_year_evidence="A", start_year_url="https://www.automateexcel.com/about/",
    start_year_note="Founded by Mark Wielgus in 2004; acquired by Steve Rynearson in 2016, per own About page.",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", 218500, "trailing_3_months", round(218500/3),
        "raw_3mo_total / 3, rounded to nearest integer", "Similarweb snapshot dated June 2026", "B",
        "https://www.similarweb.com/website/automateexcel.com/competitors/", "",
    ),
    display_ads=("N", "C", "https://www.automateexcel.com/", "None observed on homepage fetch."),
    affiliate=("UNKNOWN", UNKNOWN, UNKNOWN, "No disclosure observed in fetched content."),
    own_product=("Y", "A", "https://www.automateexcel.com/about/", "Sells \"AutoMacro\" (VBA editor/automation add-in, launched 2017, relaunched 2023)."),
    course_or_community=("Y", "A", "https://www.automateexcel.com/about/", "\"Spreadsheet Boot Camp\" interactive training."),
    newsletter_email_capture=("UNKNOWN", UNKNOWN, UNKNOWN, "Not observed in fetched excerpt."),
))

rows.append(row(
    "coefficient.io", "Coefficient (blog)",
    "SaaS company blog -- live data connector for Excel/Google Sheets; content covers spreadsheet/BI best practices",
    "Mid-scale Active Site",
    is_niche_authority="N", is_niche_authority_evidence="D",
    is_niche_authority_note="A vendor blog, not an independent content authority.",
    is_contrast_case="N", is_contrast_case_evidence="D",
    is_contrast_case_note="Flagged instead as an important traffic_scope caveat case (SaaS blog vs. whole-domain traffic), not a contrast pattern.",
    start_year=UNKNOWN, start_year_note="Not found this pass.",
    traffic=traffic_block(
        "Similarweb", "total visits", "WHOLE_DOMAIN_INCLUDES_PRODUCT", 161000, "trailing_3_months", round(161000/3),
        "raw_3mo_total / 3, rounded to nearest integer", "Similarweb snapshot dated June 2026", "B",
        "https://www.similarweb.com/website/coefficient.io/",
        "coefficient.io is the primary marketing/product domain, not a separated content-only property, so this figure includes product-page and marketing traffic, not just blog content. Traffic decreased 0.37% vs last month.",
    ),
    display_ads=("N", "D", UNKNOWN, "SaaS company blog; no display ads observed."),
    affiliate=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    own_product=("Y", "A", "https://coefficient.io/blog", "Coefficient itself is the product (no-code data platform connecting live business data to Sheets/Excel)."),
    course_or_community=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    newsletter_email_capture=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
))

rows.append(row(
    "powerpivotpro.com", "PowerPivotPro (Rob Collie / P3 Adaptive)",
    "Narrow niche authority for Power Pivot, DAX, and Power BI-in-Excel",
    "Narrow Niche Authority",
    is_niche_authority="Y", is_niche_authority_evidence="B", is_niche_authority_url="https://www.myexcelonline.com/podcast/016-excel-power-pivot-with-rob-collie-from-powerpivotpro/",
    is_niche_authority_note="Rob Collie is the ex-Microsoft Power Pivot program manager; site is widely regarded as the original evangelism hub for Power Pivot/DAX, per multiple podcast interviews.",
    is_contrast_case="N", is_contrast_case_evidence="D",
    is_contrast_case_note="Very sparse Similarweb data suggests low current measured traffic despite long history and strong reputation -- borders on low_traction_despite_age, but not enough independent confirmation to assert with confidence, so left N rather than overclaiming.",
    start_year="2010", start_year_evidence="C", start_year_url="https://powerpivotpro.com/2010/03/the-great-broken-links/",
    start_year_note="My own observation of a dated archived post URL confirms the blog existed by March 2010; exact launch date not confirmed, treated as a lower bound.",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", UNKNOWN, "", UNKNOWN, "",
        "Similarweb snapshot dated August 2026", "B",
        "https://www.similarweb.com/website/powerpivotpro.com/",
        "Similarweb page returned blank/dash placeholders for all metrics (\"insufficient data\" state); numeric value left UNKNOWN rather than guessed.",
    ),
    display_ads=("UNKNOWN", UNKNOWN, UNKNOWN, "Not directly observed this pass."),
    affiliate=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    own_product=("Y", "B", "https://www.amazon.com/dp/1615470395", "Rob Collie's company P3 Adaptive sells consulting/training built around this brand; also publishes the \"Power Pivot and Power BI\" book."),
    course_or_community=("Y", "A", "https://p3adaptive.com/2014/01/what-is-power-pivots-1-competitor/", "\"P3 Adaptive University\" training, per Rob Collie's own statement."),
    newsletter_email_capture=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
))

rows.append(row(
    "benlcollins.com", "Ben Collins (benlcollins.com)",
    "Narrow niche authority for Google Sheets and Google Apps Script",
    "Narrow Niche Authority",
    is_niche_authority="Y", is_niche_authority_evidence="B", is_niche_authority_url="https://growthinreverse.com/ben-collins/",
    is_niche_authority_note="One of the most widely cited independent Google Sheets/Apps Script educators, corroborated by a third-party creator profile.",
    is_contrast_case="N", is_contrast_case_evidence="D",
    start_year="2015", start_year_evidence="A", start_year_url="https://www.benlcollins.com/about/",
    start_year_note="Operator's own about page: \"wrote my first blog post about building dashboards in Google Sheets... in 2015\".",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", 145400, "trailing_3_months", round(145400/3),
        "raw_3mo_total / 3, rounded to nearest integer", "Similarweb snapshot dated June 2026", "B",
        "https://www.similarweb.com/website/benlcollins.com/", "",
    ),
    revenue_value=UNKNOWN, revenue_figure_period="per a Medium interview, exact date unconfirmed, likely several years old",
    revenue_note="Operator quoted directly in a third-party interview (https://medium.com/the-business-of-content/this-google-spreadsheets-guru-makes-4-000-a-month-on-online-courses-bcda90ddd9e1, tier A): \"$3,500 to $4,000 worth of online courses a month\" recurring, plus \"just shy of $8,000\" in a single launch week from 89 sales. Treated as historical, not current. [pre-950 hardening] revenue_value normalized to UNKNOWN per the Study A revenue-field policy: a compound/range figure spanning an unconfirmed historical period is not a single structured revenue_value -- preserved here in revenue_note only.",
    display_ads=("N", "D", UNKNOWN, "No display ads noted; site is course/newsletter-monetized."),
    affiliate=("UNKNOWN", UNKNOWN, UNKNOWN, "Searched for disclosure but did not find a confirming source this pass."),
    own_product=("Y", "A", "https://www.benlcollins.com/about/", "\"The Collins School of Data\" -- multiple paid courses (Modern Google Sheets, Sheets Insiders membership, Apps Script, QUERY function, Lambda functions, etc.)."),
    course_or_community=("Y", "A", "https://www.benlcollins.com/about/", "\"Sheets Insiders\" paid membership plus multiple paid courses."),
    newsletter_email_capture=("Y", "A", "https://www.benlcollins.com/about/", "\"Future Proof\" newsletter, stated 40,000+ subscribers."),
))

rows.append(row(
    "excelxor.com", "EXCELXOR (author \"XOR LX\")",
    "Narrow niche authority for advanced pure-worksheet-formula techniques in Excel (deliberately VBA-free)",
    "Narrow Niche Authority",
    is_niche_authority="Y", is_niche_authority_evidence="B", is_niche_authority_url="https://spreadsheeto.com/best-excel-blogs/",
    is_niche_authority_note="Widely cited among Excel formula specialists as an advanced formulas-only resource, listed among top Excel blogs.",
    is_contrast_case="UNKNOWN",
    is_contrast_case_note="A reader comment thread found via search implies encouragement to \"resume blogging\" (possible cadence drop), but no exact date range for a slowdown could be confirmed -- not confident enough to assert as a contrast case, so left UNKNOWN rather than guessed Y or N.",
    start_year=UNKNOWN, start_year_note="Could not confirm an exact founding year this pass.",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", UNKNOWN, "", UNKNOWN, "",
        "Similarweb snapshot dated August 2026", "B",
        "https://www.similarweb.com/website/excelxor.com/",
        "Similarweb page returned no numeric total-visits figure (dashes/blank, \"insufficient data\" state).",
    ),
    display_ads=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    affiliate=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    own_product=("N", "D", UNKNOWN, "No product found; appears purely educational."),
    course_or_community=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    newsletter_email_capture=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
))

rows.append(row(
    "ozgrid.com", "OzGrid Business Applications",
    "Excel/VBA help, forum, templates, consulting",
    "Contrast Cohort",
    is_niche_authority="Y", is_niche_authority_evidence="B", is_niche_authority_url="https://excelfox.com/forum/showthread.php/1157-Ozgrid-Website-Owner-and-Excel-Hacks-Author-Dave-Hawley-Passed-Away",
    is_niche_authority_note="One of the oldest independent Excel/VBA communities; co-founder Dave Hawley co-authored \"Excel Hacks\" and was well known in the Excel MVP community.",
    is_contrast_case="Y", is_contrast_case_evidence="A", is_contrast_case_url="https://ozgrid.com/",
    is_contrast_case_note="Co-founder Dave Hawley passed away in 2014, per OzGrid's own about page. Corroborated by two independent third-party forum threads reporting the OzGrid forum component closed effective 18 November 2025 (https://www.excelforum.com/the-water-cooler/1437775-ozgrid-is-retiring-effective-november-18-a.html, https://www.excelfox.com/forum/showthread.php/3047-quot-Ozgrid-quot-(Ozgrid-Forum)-Closed-on-Tuesday-18-November-2025). This is the forum/community component closing, not necessarily the entire ozgrid.com content site, which appeared still live.",
    contrast_pattern="cadence_drop", contrast_evidence_period="Founder passed away 2014 (per own about page); forum component confirmed closed as of 18 Nov 2025 per two independent third-party forum posts.",
    start_year="2000", start_year_evidence="A", start_year_url="https://ozgrid.com/",
    start_year_note="Own about page: \"founded by husband and wife team, Dave and Raina Hawley in 2000\".",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", UNKNOWN, "", UNKNOWN, "",
        "Similarweb snapshot dated July 2026", "B",
        "https://www.similarweb.com/website/ozgrid.com/",
        "Similarweb page shows no explicit visit-count number (dashes for engagement metrics, \"0% change vs last month\" stated).",
    ),
    display_ads=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    affiliate=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    own_product=("Y", "A", "https://ozgrid.com/", "Sells VBA/Excel consulting and templates per own homepage."),
    course_or_community=("Y", "A", "https://ozgrid.com/", "Long-running free forum (component reported closed Nov 2025 -- see is_contrast_case)."),
    newsletter_email_capture=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
))

rows.append(row(
    "spreadsheetpage.com", "The Spreadsheet Page",
    "Excel templates/tips resource; historically associated with Excel author John Walkenbach",
    "Contrast Cohort",
    is_niche_authority="UNKNOWN",
    is_niche_authority_note="Ambiguous given an apparent ownership change (Walkenbach listed only as a contributing \"writer\" currently, not credited founder in fetched content); current authority status not confirmed.",
    is_contrast_case="Y", is_contrast_case_evidence="C", is_contrast_case_url="https://spreadsheetpage.com/blog/",
    is_contrast_case_note="The site's own blog index page carries an HTML meta tag article:modified_time = 2020-07-08T08:25:28+00:00 (my own direct observation of page metadata), indicating the blog listing had not been meaningfully updated in roughly 5-6 years as of 2026. Combined with an extreme +402.4% MoM traffic swing reported by Similarweb (typical of a very-low-traffic site where small absolute changes produce large percentage swings). \"Historically strong\" is unconfirmed; the stale/declined-cadence part is the solid finding.",
    contrast_pattern="cadence_drop", contrast_evidence_period="Blog index page article:modified_time metadata = 2020-07-08; Similarweb June 2026 snapshot showed a +402.4% MoM swing consistent with a very low current baseline.",
    start_year="2006", start_year_evidence="A", start_year_url="https://spreadsheetpage.com/about/",
    start_year_note="Own about page: \"Started as a hobby site in 2006, The Spreadsheet Page grew to be one of the most popular excel template resources\". Historical Walkenbach connection unverified this pass.",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", UNKNOWN, "", UNKNOWN, "",
        "Similarweb snapshot dated June 2026", "B",
        "https://www.similarweb.com/website/spreadsheetpage.com/",
        "Page did not display a numeric total-visits figure but stated a 402.4% increase vs previous month, 38.77% bounce rate, 1.79 pages/visit -- numeric total left UNKNOWN rather than guessed.",
    ),
    display_ads=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    affiliate=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    own_product=("Y", "A", "https://spreadsheetpage.com/about/", "Described as an \"excel template resource\"."),
    course_or_community=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    newsletter_email_capture=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
))

print(f"Category 1 (Excel/Spreadsheet) rows so far: {len(rows)}")

# ============================================================
# CATEGORY 2: Personal Finance (10 sites)
# ============================================================

rows.append(row(
    "financialsamurai.com", "Financial Samurai",
    "Early retirement/FIRE, real estate, investing, career negotiation",
    "Large/Traffic Leader",
    is_niche_authority="N", is_niche_authority_evidence="D",
    is_niche_authority_note="Broad personal finance/FIRE generalist, not a single sub-methodology authority.",
    is_contrast_case="N", is_contrast_case_evidence="D",
    start_year="2009", start_year_evidence="A", start_year_url="https://www.financialsamurai.com/about/",
    start_year_note="Own about page states \"Year Started: 2009\".",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", 239200, "trailing_3_months", round(239200/3),
        "raw_3mo_total / 3, rounded to nearest integer", "Similarweb snapshot dated ~May-Jul 2026", "B",
        "https://www.similarweb.com/website/financialsamurai.com/",
        "Site also self-reports \"~550,000 organic pageviews/month\" and historically \"1.5 million organic pageviews/month\" "
        "(tier A, https://www.financialsamurai.com/how-much-do-bloggers-make-a-lot-more-than-you-think/), not reconciled with the Similarweb figure.",
    ),
    revenue_value=UNKNOWN, revenue_figure_period="various, dated (2019-era post)",
    revenue_note="Partial self-reported figures found (book \"$4,000-5,000/month\", one sponsored post \"$30,000\", consulting once \"$30,000/month\", all historical/dated) but no comprehensive current site-revenue total disclosed -- overall figure left UNKNOWN rather than assembled from fragments. Source: https://www.financialsamurai.com/how-much-do-bloggers-make-a-lot-more-than-you-think/ (tier A for the fragments themselves). [pre-950 hardening] revenue_value normalized to a clean UNKNOWN (was previously the descriptive string \"UNKNOWN (only partial historical figures found)\") per the Study A revenue-field policy: revenue_value must be either a single structured figure or exactly UNKNOWN, never a hybrid value+explanation string -- the explanation stays here in revenue_note.",
    display_ads=("Y", "A", "https://www.financialsamurai.com/about/", "Works with CafeMedia per own About page."),
    affiliate=("Y", "A", "https://www.financialsamurai.com/about/", "Fundrise, Empower, Policygenius, Amazon Associates disclosed."),
    own_product=("Y", "A", "https://www.financialsamurai.com/about/", "3 published books plus \"How to Engineer Your Layoff\" ebook (6th ed.)."),
    course_or_community=("N", "A", "https://www.financialsamurai.com/about/", "No paid course/community found; free podcast/newsletter only."),
    newsletter_email_capture=("Y", "A", "https://www.financialsamurai.com/about/", "\"60,000+ subscribers\" free weekly newsletter."),
))

rows.append(row(
    "getrichslowly.org", "Get Rich Slowly",
    "General personal finance, budgeting, debt payoff",
    "Large/Traffic Leader",
    is_niche_authority="N", is_niche_authority_evidence="D",
    is_niche_authority_note="Generalist personal-finance site.",
    is_contrast_case="Y", is_contrast_case_evidence="A", is_contrast_case_url="https://www.getrichslowly.org/how-and-why-i-sold-get-rich-slowly/",
    is_contrast_case_note="Site was sold to QuinStreet in 2009, later resold back to founder J.D. Roth; own post explicitly discusses this ownership churn. Still appears to publish currently, so this is an ownership-churn/historically_declined contrast rather than a shutdown.",
    contrast_pattern="historically_declined", contrast_evidence_period="Sold 2009 (QuinStreet), later reacquired by founder J.D. Roth; per operator's own retrospective post.",
    start_year="2006", start_year_evidence="A", start_year_url="https://www.getrichslowly.org/how-and-why-i-sold-get-rich-slowly/",
    start_year_note="Founder's own post gives the founding date as 2006-04-15.",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", UNKNOWN, "", UNKNOWN, "",
        "Similarweb snapshot dated July 2026", "B",
        "https://www.similarweb.com/website/getrichslowly.org/",
        "A clean single \"Total Visits Last 3 Months\" number could not be reliably extracted from the fetched summary (only an ambiguous \"47.3K\" comparison figure appeared) -- left UNKNOWN rather than reporting a possibly-wrong number.",
    ),
    revenue_value=UNKNOWN, revenue_note="2009 sale price to QuinStreet explicitly withheld by NDA per founder's own post (\"Because of the NDA, I can't give a number, not even a fake one\").",
    display_ads=("Y", "A", "https://www.getrichslowly.org/privacy-policy/", "Uses Mediavine for programmatic ads, per own Privacy Policy."),
    affiliate=("Y", "A", "https://www.getrichslowly.org/privacy-policy/", "\"financial relationships with some of the merchants... mentioned on this blog\"."),
    own_product=("N", "A", "https://www.getrichslowly.org/", "About page explicitly states no hard-sell products; free \"Money Boss Manifesto\" is a lead magnet, not a paid product."),
    course_or_community=("Y", "A", "https://www.getrichslowly.org/", "Active member forum (\"The Get Rich Slowly Forum\"); paid status of the forum itself is UNKNOWN, treated as Y for community existing."),
    newsletter_email_capture=("Y", "A", "https://www.getrichslowly.org/", "\"GRS Insider\" newsletter."),
))

rows.append(row(
    "whitecoatinvestor.com", "The White Coat Investor",
    "Personal finance for physicians/medical professionals",
    "Narrow Niche Authority",
    is_niche_authority="Y", is_niche_authority_evidence="B", is_niche_authority_url="https://www.acep.org/life-as-a-physician/career-center/white-coat-investor",
    is_niche_authority_note="Widely recognized (including by ACEP, the American College of Emergency Physicians) as the definitive physician-finance resource.",
    is_contrast_case="N", is_contrast_case_evidence="D",
    start_year="2011", start_year_evidence="A", start_year_url="https://www.whitecoatinvestor.com/about/",
    start_year_note="Own About page and corroborating third-party bios (e.g. ACEP) both state 2011.",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", 578900, "trailing_3_months", round(578900/3),
        "raw_3mo_total / 3, rounded to nearest integer", "Similarweb snapshot dated ~June 2026", "B",
        "https://www.similarweb.com/website/whitecoatinvestor.com/",
        "Traffic decreased 5.17% vs last month at time of lookup. Site also runs wcicourses.com and a conference as separate properties, but whitecoatinvestor.com itself is the blog/content domain.",
    ),
    revenue_value=UNKNOWN, revenue_note="Author explicitly states in a 2019 \"State of the Blog\" post that he stopped publishing specific revenue figures for privacy/competitive reasons; growth metrics (11.1M pageviews, 1.97M unique visitors in 2018) are disclosed (tier A) but not a revenue total. Source: https://www.whitecoatinvestor.com/state-of-the-blog-2019/",
    display_ads=("Y", "A", "https://www.whitecoatinvestor.com/about/", "\"advertiser and affiliate partnerships\" managed by a Director of Sales, per own About page."),
    affiliate=("Y", "A", "https://www.whitecoatinvestor.com/about/", "\"Recommended\" section connects readers to vetted financial pros/services; affiliate partnerships disclosed."),
    own_product=("Y", "A", "https://www.whitecoatinvestor.com/about/", "Books, merchandise, and annual conference (WCICON)."),
    course_or_community=("Y", "A", "https://www.whitecoatinvestor.com/about/", "Paid courses via wcicourses.com (\"Fire Your Financial Advisor\", CME courses), plus Facebook group/forum community."),
    newsletter_email_capture=("Y", "A", "https://www.whitecoatinvestor.com/about/", "Monthly newsletter plus daily post subscription."),
))

rows.append(row(
    "themilitarywallet.com", "The Military Wallet",
    "Military/veteran personal finance and benefits",
    "Narrow Niche Authority",
    is_niche_authority="Y", is_niche_authority_evidence="B", is_niche_authority_url="https://veteranonthemove.com/ryan-guina/",
    is_niche_authority_note="Long-standing, widely cited as a top military-finance resource; founder Ryan Guina interviewed on multiple military-finance podcasts/associations.",
    is_contrast_case="N", is_contrast_case_evidence="D",
    start_year=UNKNOWN, start_year_note="Precise launch year for the current domain/brand not confirmed this pass; founder's earlier related site (\"Cash Money Life\") predates it, but exact rebrand/launch year could not be verified with a real source.",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", 174000, "trailing_3_months", round(174000/3),
        "raw_3mo_total / 3, rounded to nearest integer", "Similarweb snapshot dated ~July 2026", "B",
        "https://www.similarweb.com/website/themilitarywallet.com/",
        "Traffic increased 6.39% vs last month at time of lookup.",
    ),
    display_ads=("Y", "A", "https://themilitarywallet.com/about/", "\"may receive compensation through advertising placements\" per own About page."),
    affiliate=("Y", "A", "https://themilitarywallet.com/about/", "\"corporate affiliate\" partner relationships disclosed."),
    own_product=("UNKNOWN", UNKNOWN, UNKNOWN, "None found on About page."),
    course_or_community=("UNKNOWN", UNKNOWN, UNKNOWN, "None found."),
    newsletter_email_capture=("Y", "A", "https://themilitarywallet.com/about/", "Weekly email signup (\"Weekly wisdom you can read in 5 minutes\")."),
))

rows.append(row(
    "dividendgrowthinvestor.com", "Dividend Growth Investor",
    "Dividend growth investing strategy (narrow investing sub-methodology)",
    "Narrow Niche Authority",
    is_niche_authority="Y", is_niche_authority_evidence="B", is_niche_authority_url="https://bloggers.feedspot.com/dividend_blogs/",
    is_niche_authority_note="One of the longest-running, most-cited sites specifically for the \"dividend growth investing\" strategy; appears in dividend-blog roundups and is referenced by other DGI bloggers.",
    is_contrast_case="N", is_contrast_case_evidence="D",
    is_contrast_case_note="Long-running but no evidence of decline found; appears to still be actively monetizing via a paid newsletter.",
    start_year="2008", start_year_evidence="A", start_year_url="https://www.dividendgrowthinvestor.com/2018/01/investing-lessons-learned-from-ten.html",
    start_year_note="Author's own post states \"Today marks the 15th birthday of the Dividend Growth Investor blog\" (dated Jan 2023, implying 2008 start); footer copyright also reads 2008-2023.",
    traffic=traffic_block(
        "Similarweb", "global rank change only", "CONTENT_ONLY", UNKNOWN, "", UNKNOWN, "",
        "Similarweb snapshot, lookup 2026-09-17", "B",
        "https://www.similarweb.com/website/dividendgrowthinvestor.com/",
        "Only global-rank change was legible (rank improved ~2.7M to ~2.4M over 3 months, \"Last Month Change: 35.32%\"); no clean absolute visits total extracted -- left UNKNOWN. Rank in the 2-3 million range indicates a genuinely small/niche site.",
    ),
    display_ads=("Y", "C", "https://www.dividendgrowthinvestor.com/p/dividend-growth-investor-newsletter.html", "Page metadata shows a Google AdSense host-account tag on the newsletter page (direct technical observation)."),
    affiliate=("UNKNOWN", UNKNOWN, UNKNOWN, "Not directly confirmed in fetched content."),
    own_product=("Y", "A", "https://www.dividendgrowthinvestor.com/p/dividend-growth-investor-newsletter.html", "Paid newsletter ($7/month or $75/year) offering a model dividend portfolio."),
    course_or_community=("N", "D", UNKNOWN, "Product is a newsletter, not a course/community."),
    newsletter_email_capture=("Y", "A", "https://www.dividendgrowthinvestor.com/p/dividend-growth-investor-newsletter.html", "Paid newsletter tier confirmed; free capture likely but not separately confirmed."),
))

rows.append(row(
    "frugalwoods.com", "Frugalwoods",
    "Extreme frugality + FIRE, homesteading lifestyle",
    "Mid-scale Active Site",
    is_niche_authority="N", is_niche_authority_evidence="D",
    is_niche_authority_note="Well-known FIRE/frugality blog but not tied to one specific named sub-methodology beyond general extreme frugality.",
    is_contrast_case="N", is_contrast_case_evidence="D",
    is_contrast_case_note="9-year retrospective shows continued active publishing (718 posts by 2023), no evidence of decline.",
    start_year="2014", start_year_evidence="A", start_year_url="https://frugalwoods.com/2023/04/07/reflecting-on-nine-years-of-frugalwoods/",
    start_year_note="Self-stated: \"When I started Frugalwoods on April 9, 2014, I had just turned 30\".",
    traffic=traffic_block(
        "Similarweb", "total visits (ambiguous)", "CONTENT_ONLY", UNKNOWN, "", UNKNOWN, "",
        "Similarweb snapshot, lookup 2026-09-17", "B",
        "https://www.similarweb.com/website/frugalwoods.com/",
        "Only an ambiguous \"14K\" comparison figure surfaced with no clear period label -- left UNKNOWN rather than reporting a possibly-wrong number.",
    ),
    revenue_value=UNKNOWN, revenue_note="No income figures disclosed; monetizes via \"financial consulting\" services and book sales, no dollar figures found.",
    display_ads=("N", "A", "https://frugalwoods.com/recommendations/", "Explicit operator statement: \"Ever wonder why you don't see ads here on Frugalwoods? That's because... I refuse to promote crap\" -- rare explicit negative confirmation."),
    affiliate=("Y", "A", "https://frugalwoods.com/recommendations/", "Explicit disclosure: \"Frugalwoods will receive some cash money if you sign up... using my links\"."),
    own_product=("Y", "A", "https://frugalwoods.com/about/", "Book \"Meet the Frugalwoods\"; paid \"Hire Me\" financial consulting."),
    course_or_community=("Y", "A", "https://frugalwoods.com/about/", "Free \"Uber Frugal Month Challenge\" lead magnet plus paid 1:1 financial consulting; no group course/paid community confirmed."),
    newsletter_email_capture=("Y", "A", "https://frugalwoods.com/about/", "\"Join my Email List\" on About page."),
))

rows.append(row(
    "esimoney.com", "ESI Money",
    "Millionaire wealth-building interviews, FI through \"Earn-Save-Invest\" framework",
    "Mid-scale Active Site",
    is_niche_authority="Y", is_niche_authority_evidence="B", is_niche_authority_url="https://www.physicianonfire.com/esimoney/",
    is_niche_authority_note="Recognized as THE go-to source for its specific \"Millionaire Interview\" series format (400+ interviews); format widely referenced/reused by other FI bloggers.",
    is_contrast_case="N", is_contrast_case_evidence="D",
    start_year="2016", start_year_evidence="A", start_year_url="https://esimoney.com/about/",
    start_year_note="Own About page: \"I started ESI Money shortly before I retired\" (retirement occurred fall 2016, confirmed via a separate own post \"I Retired!!!\").",
    traffic=traffic_block(
        "Similarweb", "total visits (ambiguous)", "CONTENT_ONLY", UNKNOWN, "", UNKNOWN, "",
        "Similarweb snapshot, lookup 2026-09-17", "B",
        "https://www.similarweb.com/website/esimoney.com/",
        "Numbers were not cleanly extractable (\"21.2K\" appeared as an ambiguous/placeholder figure); \"traffic increased by 28.67% month-over-month\" was legible -- absolute visits left UNKNOWN.",
    ),
    display_ads=("N", "C", "https://esimoney.com/", "Not observed on homepage fetch (not exhaustive)."),
    affiliate=("Y", "C", "https://esimoney.com/", "Amazon affiliate tracking tags observed in links (e.g. \"tag=wealio-20\")."),
    own_product=("UNKNOWN", UNKNOWN, UNKNOWN, "No standalone product found beyond the paid community below."),
    course_or_community=("Y", "A", "https://esimoney.com/introducing-the-millionaire-money-mentors/", "\"Millionaire Money Mentors\" paid membership community with mentors, forums, book club; confirmed paid via stated sale/intro-rate promos."),
    newsletter_email_capture=("Y", "A", "https://esimoney.com/", "\"email series\" signup."),
))

rows.append(row(
    "budgetsaresexy.com", "Budgets Are Sexy",
    "General personal finance/budgeting, blogging-business commentary",
    "Contrast Cohort",
    is_niche_authority="N", is_niche_authority_evidence="D",
    is_niche_authority_note="General PF blog; founder also created Rockstar Finance (a related but separate PF blog directory).",
    is_contrast_case="Y", is_contrast_case_evidence="A", is_contrast_case_url="https://budgetsaresexy.com/j-money-is-back/",
    is_contrast_case_note="Site was sold to The Motley Fool in 2019, went dormant/steward-only for ~3 years; founder explicitly states upon his 2022 return that \"traffic/readership have dropped precipitously\" during the gap.",
    contrast_pattern="shutdown", contrast_evidence_period="Sold 2019, dormant/steward-managed ~2019-2022, founder's own 2022 return post states traffic/readership dropped precipitously during that gap.",
    start_year="2008", start_year_evidence="A", start_year_url="https://budgetsaresexy.com/about/",
    start_year_note="Own About page: \"back in 2008 in my 20s\" (stated Feb 2008).",
    traffic=traffic_block(
        "Similarweb", "total visits (ambiguous)", "CONTENT_ONLY", UNKNOWN, "", UNKNOWN, "",
        "Similarweb snapshot, lookup 2026-09-17", "B",
        "https://www.similarweb.com/website/budgetsaresexy.com/",
        "Only an ambiguous \"65.2K\" comparison figure surfaced with unclear period -- left UNKNOWN.",
    ),
    revenue_value=UNKNOWN, revenue_note="No dollar figures found, though \"30,000,000+ views\" and \"130,000+ comments\" lifetime engagement stats are disclosed on own About page (tier A) -- these are engagement stats, not revenue.",
    display_ads=("Y", "A", "https://budgetsaresexy.com/about/", "Self-stated: \"advertisers started showing up and asking if they can give me money to display an ad\"."),
    affiliate=("Y", "A", "https://budgetsaresexy.com/about/", "Affiliate links to apps/books/investing platforms confirmed on own About page."),
    own_product=("UNKNOWN", UNKNOWN, UNKNOWN, "No distinct product found beyond services below."),
    course_or_community=("Y", "A", "https://budgetsaresexy.com/about/", "\"blog coaching, fintech coaching, and speaking services\" offered."),
    newsletter_email_capture=("Y", "A", "https://budgetsaresexy.com/about/", "Weekly Friday newsletter."),
))

rows.append(row(
    "consumerismcommentary.com", "Consumerism Commentary",
    "General personal finance/consumer finance commentary",
    "Contrast Cohort",
    is_niche_authority="N", is_niche_authority_evidence="D",
    is_niche_authority_note="Site's own recorded primary_niche is general personal finance/consumer finance "
                             "commentary, not a specific named sub-niche, and the domain is now shut down "
                             "(contrast_pattern=shutdown) -- neither is consistent with being a current niche "
                             "authority.",
    is_contrast_case="Y", is_contrast_case_evidence="C", is_contrast_case_url="https://robberger.com/welcome-consumerism-commentary-and-five-cent-nickel-readers/",
    is_contrast_case_note="Currently 302-redirects to a page where owner Rob Berger states he \"closed ConsumerismCommentary.com and redirected it\" because running multiple websites was too much (operator's own stated reason, tier A content on a tier-C-observed live redirect).",
    contrast_pattern="shutdown", contrast_evidence_period="Founded 2003 (per QuinStreet's 2011 acquisition press release); acquired by QuinStreet Nov 2011; later reacquired by Rob Berger; live redirect to shutdown-announcement page observed 2026-09-17.",
    start_year="2003", start_year_evidence="B", start_year_url="https://www.globenewswire.com/news-release/2011/11/28/462419/239253/en/QuinStreet-Announces-Acquisition-of-ConsumerismCommentary-com.html",
    start_year_note="QuinStreet's own acquisition press release states the site was \"created in 2003 by Luke Landes\".",
    traffic=traffic_block(
        UNKNOWN, UNKNOWN, UNKNOWN, UNKNOWN, "", UNKNOWN, "",
        "", UNKNOWN, UNKNOWN,
        "Domain is no longer independently operational (see contrast case); no live traffic figure is meaningful or applicable.",
    ),
    display_ads=("UNKNOWN", UNKNOWN, UNKNOWN, "Historical; site no longer operates standalone."),
    affiliate=("UNKNOWN", UNKNOWN, UNKNOWN, "Historical; site no longer operates standalone."),
    own_product=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    course_or_community=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    newsletter_email_capture=("N", "C", "https://robberger.com/welcome-consumerism-commentary-and-five-cent-nickel-readers/", "Domain now hard-redirects to a newsletter signup for a different brand (RobBerger.com), not its own."),
))

rows.append(row(
    "1500days.com", "1500 Days to Freedom",
    "FIRE / early retirement, portfolio performance tracking",
    "Contrast Cohort",
    is_niche_authority="N", is_niche_authority_evidence="D",
    is_niche_authority_note="Generalist FIRE blog, well-known but not tied to one specific named sub-methodology.",
    is_contrast_case="Y", is_contrast_case_evidence="C", is_contrast_case_url="https://www.1500days.com/all-posts/",
    is_contrast_case_note="Direct comparison of the site's own archive shows a shift from multiple weekly/near-daily posts in 2013-2016 to sparse, quarterly \"Performance Update\" posts by 2020-2025, corroborated by a 22.53% recent month-over-month traffic decline per Similarweb.",
    contrast_pattern="cadence_drop", contrast_evidence_period="Weekly/near-daily posting 2013-2016 per own archive pattern vs. quarterly \"Performance Update\" posts by 2020-2025 (e.g. Q1 2025 update); 22.53% MoM traffic decline per Similarweb, lookup 2026-09-17.",
    start_year=UNKNOWN, start_year_note="Site clearly predates 2016 based on early archive content, but no stated founding year found with a citable URL this pass.",
    traffic=traffic_block(
        "Similarweb", "total visits (ambiguous)", "CONTENT_ONLY", UNKNOWN, "", UNKNOWN, "",
        "Similarweb snapshot, lookup 2026-09-17", "B",
        "https://www.similarweb.com/website/1500days.com/",
        "Ambiguous \"19.4K\" comparison figure with \"traffic decreased 22.53% compared to last month\" -- decline direction legible, absolute total left UNKNOWN.",
    ),
    display_ads=("UNKNOWN", UNKNOWN, UNKNOWN, "Not confirmed either way in fetched content."),
    affiliate=("Y", "A", "https://www.1500days.com/money-saving-products/", "\"Stuff We Like\" page contains affiliate links (Bluehost, Personal Capital, Fundrise, PeerStreet, LendingTree, Ting) with disclosure \"some of these links help support the blog\"."),
    own_product=("N", "D", UNKNOWN, "Not observed; site publishes net-worth/portfolio updates, not a sold product."),
    course_or_community=("N", "D", UNKNOWN, "Not observed."),
    newsletter_email_capture=("UNKNOWN", UNKNOWN, UNKNOWN, "Not directly confirmed."),
))

print(f"Category 2 (Personal Finance) rows so far: {len(rows)}")

# ============================================================
# CATEGORY 3: Home/DIY & Food/Recipe (10 sites)
# ============================================================

rows.append(row(
    "apartmenttherapy.com", "Apartment Therapy",
    "Home decor/organization media",
    "Large/Traffic Leader",
    is_niche_authority="N", is_niche_authority_evidence="D",
    is_niche_authority_note="Broad home-decor media, not a single sub-topic authority.",
    is_contrast_case="N", is_contrast_case_evidence="D",
    start_year="2004", start_year_evidence="B", start_year_url="https://en.wikipedia.org/wiki/Apartment_Therapy",
    start_year_note="Founder Maxwell Ryan turned his 2001 design-consultancy newsletter into a daily blog with brother Oliver in 2004, per Wikipedia.",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", 6400000, "trailing_3_months", round(6400000/3),
        "raw_3mo_total / 3, rounded to nearest integer", "Similarweb snapshot, lookup 2026-09-17", "B",
        "https://www.similarweb.com/website/apartmenttherapy.com/",
        "Down 15% vs prior month, global rank #10,977.",
    ),
    revenue_value=UNKNOWN, revenue_note="Adweek notes a \"26% revenue pop from sticky sponsored tools\" but no absolute dollar figure. Source: https://www.adweek.com/media/apartment-therapy-revenue-sticky-sponsored-tools/",
    display_ads=("Y", "B", "https://advertising.apartmenttherapy.com/apartmenttherapy.html", "Runs a dedicated ad-sales operation."),
    affiliate=("Y", "D", UNKNOWN, "Inferred from \"What to Buy\"/shopping content; not a direct disclosure quote."),
    own_product=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    course_or_community=("Y", "C", "https://www.apartmenttherapy.com/features/the-cure-program", "\"The Cure\" program observed."),
    newsletter_email_capture=("Y", "C", "https://www.apartmenttherapy.com/", "Signup forms observed."),
))

rows.append(row(
    "seriouseats.com", "Serious Eats",
    "Food journalism/recipes/food science",
    "Large/Traffic Leader",
    is_niche_authority="Y", is_niche_authority_evidence="B", is_niche_authority_url="https://en.wikipedia.org/wiki/Serious_Eats",
    is_niche_authority_note="\"The Food Lab\" column is the recognized reference for food-science-based cooking, per Wikipedia.",
    is_contrast_case="N", is_contrast_case_evidence="D",
    start_year=UNKNOWN, start_year_note="Wikipedia excerpt fetched did not state an explicit founding year; commonly cited elsewhere as ~2006 but not verified with a direct URL this pass, so left UNKNOWN rather than guessed.",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", 22600000, "trailing_3_months", round(22600000/3),
        "raw_3mo_total / 3, rounded to nearest integer", "Similarweb snapshot, lookup 2026-09-17", "B",
        "https://www.similarweb.com/website/seriouseats.com/",
        "Down 5.96% vs prior month, global rank ~2,520.",
    ),
    revenue_value=UNKNOWN, revenue_note="Owned by Dotdash Meredith; no per-site figure disclosed.",
    display_ads=("Y", "B", "https://www.advertise-with-us.com/p/418552", "Dotdash Meredith runs its own ad network/programmatic sales for the site."),
    affiliate=("UNKNOWN", UNKNOWN, UNKNOWN, "Direct page fetch was blocked; not independently confirmed this pass."),
    own_product=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    course_or_community=("N", "D", UNKNOWN, "No evidence found."),
    newsletter_email_capture=("UNKNOWN", UNKNOWN, UNKNOWN, "Fetch blocked."),
))

rows.append(row(
    "designsponge.com", "Design*Sponge",
    "Interior design/DIY blog (defunct)",
    "Contrast Cohort",
    is_niche_authority="Y", is_niche_authority_evidence="B", is_niche_authority_url="https://businessofhome.com/articles/behind-grace-bonney-s-decision-to-close-design-sponge",
    is_niche_authority_note="Was a defining voice in independent design blogging, per Business of Home retrospective.",
    is_contrast_case="Y", is_contrast_case_evidence="A", is_contrast_case_url="https://businessofhome.com/articles/behind-grace-bonney-s-decision-to-close-design-sponge",
    is_contrast_case_note="Founder Grace Bonney explicitly closed the site Aug 30, 2019, citing refusal to increase sponsored/celebrity content to stay profitable (operator's own stated reason, quoted in a third-party piece).",
    contrast_pattern="shutdown", contrast_evidence_period="Site closed by founder's own decision, announced/effective Aug 30, 2019.",
    start_year="2004", start_year_evidence="B", start_year_url="https://businessofhome.com/articles/behind-grace-bonney-s-decision-to-close-design-sponge",
    start_year_note="Business of Home reports the site closed \"15 years\" after its launch, with closure announced in 2019, implying a ~2004 launch.",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", UNKNOWN, "", UNKNOWN, "",
        "", UNKNOWN, UNKNOWN,
        "No current traffic figure sought since the domain is inactive as an original content property (closed Aug 30, 2019). traffic_scope is nonetheless CONTENT_ONLY as a domain-structure judgment (Design*Sponge was historically a content/media property, not a SaaS/app domain) -- independent of the fact that no current traffic value applies. [pre-950 hardening] scope reclassified from a bare UNKNOWN default to CONTENT_ONLY per the corrected traffic_scope definition (domain structure, not data availability).",
    ),
    revenue_value=UNKNOWN, revenue_note="No dollar figures disclosed. At peak, founder self-reported \"over 2 million readers per month\" (tier A, quoted in the Business of Home piece) -- an audience figure, not revenue.",
    display_ads=("UNKNOWN", UNKNOWN, UNKNOWN, "Site inactive since Aug 30, 2019; not assessed."),
    affiliate=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    own_product=("Y", "D", UNKNOWN, "Historically sold books/products under the Design*Sponge brand."),
    course_or_community=("N", "D", UNKNOWN,
                          "Site has been inactive as an original content property since closing Aug 30, 2019 "
                          "(contrast_pattern=shutdown); no course or community offering could plausibly be "
                          "operating on a domain that stopped publishing years ago."),
    newsletter_email_capture=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
))

rows.append(row(
    "101cookbooks.com", "101 Cookbooks",
    "Vegetarian/whole-foods recipes",
    "Contrast Cohort",
    is_niche_authority="Y", is_niche_authority_evidence="B", is_niche_authority_url="https://techland.time.com/2013/08/05/the-25-best-bloggers-2013-edition/slide/heidi-swanson-101-cookbooks/",
    is_niche_authority_note="One of the earliest/most recognized food blogs; named to TIME's \"25 Best Bloggers\" 2013.",
    is_contrast_case="Y", is_contrast_case_evidence="C", is_contrast_case_url="https://www.101cookbooks.com/",
    is_contrast_case_note="Site is 23 years old and was a TIME-recognized top blog, yet current traffic (~261K/mo) is far below newer peers of similar or shorter tenure (e.g. loveandlemons.com at ~13.8M/3mo, started 2012). Current RSS feed shows only ~1 post per 1-3 weeks (8 posts spanning ~3 months, June-Sept 2026), a markedly reduced cadence versus the site's historically frequent early-2000s posting described in profile pieces.",
    contrast_pattern="cadence_drop", contrast_evidence_period="Current (Sept 2026) posting cadence vs. historical reputation as a top-tier blog and TIME's 2013 recognition.",
    start_year="2003", start_year_evidence="A", start_year_url="https://www.101cookbooks.com/about",
    start_year_note="Own about page: \"101 Cookbooks started in early 2003\".",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", 783500, "trailing_3_months", round(783500/3),
        "raw_3mo_total / 3, rounded to nearest integer", "Similarweb snapshot, lookup 2026-09-17", "B",
        "https://www.101cookbooks.com/", "Up 4.34% vs prior month, global rank #80,295.",
    ),
    revenue_value=UNKNOWN, revenue_note="No figures disclosed.",
    display_ads=("UNKNOWN", UNKNOWN, UNKNOWN, "Site markets a paid membership with \"ad-free content\" as a benefit, implying the free tier carries some ads, but this is a mixed/indirect signal rather than a direct observation, so left UNKNOWN rather than asserted Y."),
    affiliate=("Y", "C", "https://www.101cookbooks.com/", "Explicit Amazon Associates disclosure observed on-site."),
    own_product=("Y", "C", "https://www.101cookbooks.com/", "Multiple published cookbooks (Super Natural Simple, Near & Far, etc.)."),
    course_or_community=("Y", "C", "https://www.101cookbooks.com/", "Paid membership (\"ad-free content\", bonus PDFs)."),
    newsletter_email_capture=("Y", "C", "https://www.101cookbooks.com/", "\"Join my newsletter!\" observed."),
))

rows.append(row(
    "shanty-2-chic.com", "Shanty 2 Chic",
    "DIY furniture building plans",
    "Mid-scale Active Site",
    is_niche_authority="N", is_niche_authority_evidence="D",
    is_niche_authority_note="Mid-tier DIY furniture blog, not the singular reference site.",
    is_contrast_case="N", is_contrast_case_evidence="D",
    is_contrast_case_note="Traffic declining slightly (-1.82% MoM) but not dramatically; not treated as a contrast case.",
    start_year="2009", start_year_evidence="C", start_year_url="https://www.shanty-2-chic.com/about/",
    start_year_note="Own about content states the site launched in August 2009.",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", 40300, "trailing_3_months", round(40300/3),
        "raw_3mo_total / 3, rounded to nearest integer", "Similarweb snapshot, lookup 2026-09-17", "B",
        "https://www.similarweb.com/website/shanty-2-chic.com/",
        "Down 1.82% vs prior month; category rank #312 Home Improvement (US).",
    ),
    revenue_value=UNKNOWN, revenue_note="A third-party influencer-marketing estimator tool suggested a \"$3 million net worth\" figure, but this is an unverified estimate of unclear methodology, not disclosed revenue -- not used as a finding.",
    display_ads=("UNKNOWN", UNKNOWN, UNKNOWN, "Not directly observed in fetched excerpt."),
    affiliate=("Y", "D", UNKNOWN, "Inferred from \"Shop Our Favorite Finds\" product-recommendation pages; not a direct disclosure quote."),
    own_product=("Y", "B", "https://www.dallasnews.com/business/retail/2018/01/16/plano-retailer-at-home-partners-with-fort-worth-sisters-who-built-a-furniture-following-online/", "Shanty2Chic Home Collection sold at At Home stores nationwide, per Dallas News."),
    course_or_community=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    newsletter_email_capture=("Y", "C", "https://www.shanty-2-chic.com/", "\"VIP Insider\" signup observed."),
))

rows.append(row(
    "tinyhousetalk.com", "Tiny House Talk",
    "Tiny house movement (curation/news)",
    "Narrow Niche Authority",
    is_niche_authority="Y", is_niche_authority_evidence="D",
    is_niche_authority_note="Widely cited as one of the original/definitive tiny-house-movement news/curation sites since 2009; reasoned from long tenure plus niche specificity, not a third-party ranking source.",
    is_contrast_case="N", is_contrast_case_evidence="D",
    is_contrast_case_note="Declining slightly (-3.57% MoM) but not dramatic enough alone; used as the niche-authority slot instead.",
    start_year="2009", start_year_evidence="C", start_year_url="https://tinyhousetalk.com/about/",
    start_year_note="Own about page states founding by Alex Pino in 2009 (my own direct observation of the page).",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", 99500, "trailing_3_months", round(99500/3),
        "raw_3mo_total / 3, rounded to nearest integer", "Similarweb snapshot, lookup 2026-09-17", "B",
        "https://www.similarweb.com/website/tinyhousetalk.com/",
        "Down 3.57% vs prior month, global rank #406,197, category #1,727 Home & Garden.",
    ),
    revenue_value=UNKNOWN, revenue_note="No figures found.",
    display_ads=("UNKNOWN", UNKNOWN, UNKNOWN, "Not directly confirmed; affiliate confirmed separately."),
    affiliate=("Y", "C", "https://tinyhousetalk.com/", "Explicit Amazon Associates disclosure observed on-site."),
    own_product=("N", "D", UNKNOWN, "Offers free plans/eBooks, not sold products."),
    course_or_community=("N", "D", UNKNOWN,
                          "Site's content model (per its recorded primary_niche) is curation/news aggregation of "
                          "other people's tiny houses, not a personal-brand teaching site; no course or paid "
                          "community was identified alongside its free plans/eBooks and affiliate/ad monetization."),
    newsletter_email_capture=("Y", "C", "https://tinyhousetalk.com/", "\"Tiny House Newsletter\" via ConvertKit observed."),
))

rows.append(row(
    "loveandlemons.com", "Love and Lemons",
    "Vegetarian recipes",
    "Mid-scale Active Site",
    is_niche_authority="N", is_niche_authority_evidence="D",
    is_niche_authority_note="Broad vegetarian recipe site, strong but not narrow-topic definitive.",
    is_contrast_case="N", is_contrast_case_evidence="D",
    start_year="2012", start_year_evidence="B", start_year_url="https://www.nichepursuits.com/love-and-lemons-success-story/",
    start_year_note="Third-party profile: \"Since the site started in 2012...\".",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", 13800000, "trailing_3_months", round(13800000/3),
        "raw_3mo_total / 3, rounded to nearest integer", "Similarweb snapshot, lookup 2026-09-17", "B",
        "https://www.similarweb.com/website/loveandlemons.com/",
        "Up 4.25% vs prior month, category rank #16 Cooking & Recipes (US). A third-party profile separately cited \"10M visitors/month\" as of 2022/2023 (tier B, different period, https://www.nichepursuits.com/love-and-lemons-success-story/), not reconciled with this snapshot.",
    ),
    revenue_value=UNKNOWN, revenue_note="Not disclosed in sources found.",
    display_ads=("Y", "B", "https://www.nichepursuits.com/love-and-lemons-success-story/", "Confirmed in a third-party profile (\"sidebar and in-content placements\")."),
    affiliate=("Y", "B", "https://www.nichepursuits.com/love-and-lemons-success-story/", "\"affiliate sales through resources shop\", per third-party profile."),
    own_product=("Y", "B", "https://www.nichepursuits.com/love-and-lemons-success-story/", "Two published cookbooks plus a recipe planner."),
    course_or_community=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    newsletter_email_capture=("Y", "C", "https://loveandlemons.substack.com/", "Substack newsletter confirmed."),
))

rows.append(row(
    "theperfectloaf.com", "The Perfect Loaf",
    "Sourdough baking (technique/science)",
    "Narrow Niche Authority",
    is_niche_authority="Y", is_niche_authority_evidence="B", is_niche_authority_url="https://pastryartsmag.com/people/maurizio-leo-a-sourdough-masters-quest-for-the-perfect-loaf/",
    is_niche_authority_note="James Beard Award-winning, NYT bestseller sourdough resource; widely cited as the go-to sourdough-science site.",
    is_contrast_case="N", is_contrast_case_evidence="D",
    is_contrast_case_note="A -25.56% MoM traffic dip is real but is a single-month reading, not a verified sustained decline pattern.",
    start_year="2012", start_year_evidence="C", start_year_url="https://www.theperfectloaf.com/about/",
    start_year_note="Own about page states the site was \"established in 2012\".",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", 475000, "trailing_3_months", round(475000/3),
        "raw_3mo_total / 3, rounded to nearest integer", "Similarweb snapshot, lookup 2026-09-17", "B",
        "https://www.similarweb.com/website/theperfectloaf.com/",
        "Down 25.56% vs prior month, global rank fell #91,021 to #112,350.",
    ),
    revenue_value=UNKNOWN, revenue_note="Multiple revenue streams identified (books, membership, workshops) but not individually quantified.",
    display_ads=("N", "C", "https://www.theperfectloaf.com/about/", "Site explicitly describes itself as maintaining an \"ad-free model\"."),
    affiliate=("Y", "C", "https://www.theperfectloaf.com/", "\"Amazon Influencer\" -- earns from qualifying purchases."),
    own_product=("Y", "B", "https://pastryartsmag.com/people/maurizio-leo-a-sourdough-masters-quest-for-the-perfect-loaf/", "Two published books (The Perfect Loaf -- NYT bestseller and James Beard Award winner; The Perfect Pizza)."),
    course_or_community=("Y", "C", "https://www.theperfectloaf.com/", "\"The Baker's Corner\" paid membership plus paid workshops/baking trips."),
    newsletter_email_capture=("UNKNOWN", UNKNOWN, UNKNOWN, "Not directly confirmed in fetched excerpt."),
))

rows.append(row(
    "afarmgirlsdabbles.com", "A Farmgirl's Dabbles",
    "Home-cooking/family recipes",
    "Mid-scale Active Site",
    is_niche_authority="N", is_niche_authority_evidence="D",
    is_niche_authority_note="Site's own recorded primary_niche is general home-cooking/family recipes, a broad "
                             "category rather than a specific named sub-niche, so it was not treated as a narrow "
                             "niche authority.",
    start_year="2010", start_year_evidence="A", start_year_url="https://www.afarmgirlsdabbles.com/about/",
    start_year_note="Operator's own statement: \"I started A Farmgirl's Dabbles in 2010\".",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", 215900, "trailing_3_months", round(215900/3),
        "raw_3mo_total / 3, rounded to nearest integer", "Similarweb snapshot, lookup 2026-09-17", "B",
        "https://www.similarweb.com/website/afarmgirlsdabbles.com/",
        "Down 16.41% vs prior month, global rank fell #198,515 to #224,964. Borderline decline signal, but not selected as the primary contrast case for this batch.",
    ),
    revenue_value=UNKNOWN, revenue_note="Not disclosed.",
    display_ads=("UNKNOWN", UNKNOWN, UNKNOWN, "Not directly observed in fetched homepage excerpt."),
    affiliate=("Y", "D", UNKNOWN, "Inferred from a \"Privacy & Disclosure\" footer link plus recipe-post affiliate-link references; not a direct disclosure quote captured."),
    own_product=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    course_or_community=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    newsletter_email_capture=("Y", "C", "https://www.afarmgirlsdabbles.com/", "\"get new recipes via email\" forms observed."),
))

rows.append(row(
    "thewoodwhisperer.com", "The Wood Whisperer",
    "Woodworking instruction/video",
    "Narrow Niche Authority",
    is_niche_authority="Y", is_niche_authority_evidence="D",
    is_niche_authority_note="One of the longest-running, most-cited video-based woodworking education brands (founded 2006, spawned dedicated Guild + podcast); reasoned from tenure and brand extensions, not a third-party ranking source.",
    is_contrast_case="N", is_contrast_case_evidence="D",
    start_year="2006", start_year_evidence="C", start_year_url="https://thewoodwhisperer.com/about/",
    start_year_note="Own about page states founding by Marc Spagnuolo in 2006 (my own direct observation of the page).",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", 121500, "trailing_3_months", round(121500/3),
        "raw_3mo_total / 3, rounded to nearest integer", "Similarweb snapshot, lookup 2026-09-17", "B",
        "https://www.similarweb.com/website/thewoodwhisperer.com/",
        "Up 5.58% vs prior month. Note: Similarweb mis-categorized this site under \"Social Media Networks\" -- likely a data-quality quirk on Similarweb's side, flagged for transparency.",
    ),
    revenue_value=UNKNOWN, revenue_note="Not disclosed.",
    display_ads=("Y", "C", "https://thewoodwhisperer.com/about/", "Site discloses use of \"analytics and advertisement cookies\"."),
    affiliate=("Y", "C", "https://thewoodwhisperer.com/about/", "Explicit disclosure: \"assume that any links leading you to products or services are affiliate links\"."),
    own_product=("Y", "C", "https://thewoodwhisperer.com/about/", "Books (\"Hybrid Woodworking\", \"Essential Joinery\"), merchandise, and supplies via the TWW Store."),
    course_or_community=("Y", "C", "https://thewoodwhisperer.com/about/", "\"The Wood Whisperer Guild\" paid membership (thewoodwhispererguild.com)."),
    newsletter_email_capture=("UNKNOWN", UNKNOWN, UNKNOWN, "Not directly confirmed."),
))

print(f"Category 3 (Home/DIY & Food/Recipe -- un-merged into 'Home / DIY' x5 and 'Food / Recipe' x5 "
      f"via schema_extend.DOMAIN_CATEGORY_OVERRIDES, last pre-950 patch) rows so far: {len(rows)}")

# ============================================================
# CATEGORY 4: Product Review / Buying Guides (10 sites)
# ============================================================

rows.append(row(
    "pcmag.com", "PCMag",
    "Tech product reviews & buying guides (broad consumer electronics/software)",
    "Large/Traffic Leader",
    is_niche_authority="N", is_niche_authority_evidence="D",
    is_niche_authority_note="Broad tech category, not a single narrow product niche.",
    is_contrast_case="N", is_contrast_case_evidence="D",
    start_year="1982", start_year_evidence="B", start_year_url="https://en.wikipedia.org/wiki/PCMag",
    start_year_note="Founded 1982 as PC Magazine (print); went online-only Jan 2009, per Wikipedia and corroborating Forbes 2008 coverage of the print shutdown.",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", 11400000, "trailing_3_months", round(11400000/3),
        "raw_3mo_total / 3, rounded to nearest integer", "Similarweb snapshot dated ~August 2026", "B",
        "https://www.similarweb.com/website/pcmag.com/",
        "traffic_scope left UNKNOWN rather than guessed CONTENT_ONLY -- PCMag hosts software/VPN test tools that may not be separable from editorial content traffic.",
    ),
    revenue_value=UNKNOWN, revenue_note="Parent Ziff Davis discloses a company-wide \"$1 billion affiliate commerce business\" (https://www.adexchanger.com/the-sell-sider/inside-the-data-crunching-that-powers-ziff-media-groups-1-billion-affiliate-commerce-biz/, tier B) but this is not PCMag-specific, so site-level revenue is UNKNOWN.",
    display_ads=("Y", "D", UNKNOWN, "Reasoned inference (well documented industry-wide for this publisher); homepage fetch was blocked so not independently re-observed this pass."),
    affiliate=("Y", "B", "https://www.websiterating.com/vpn/pcmag-vpn-conflict-of-interest-ziff-davis/", "PCMag runs \"Editors' Choice\"/buying-guide affiliate links; documented in third-party coverage of Ziff Davis's affiliate commerce practices."),
    own_product=("N", "D", UNKNOWN, "No evidence found of PCMag selling its own physical product."),
    course_or_community=("UNKNOWN", UNKNOWN, UNKNOWN, "Not found."),
    newsletter_email_capture=("Y", "D", UNKNOWN, "Reasoned inference (well known industry-wide); homepage fetch blocked so not independently re-verified this pass."),
))

rows.append(row(
    "tomsguide.com", "Tom's Guide",
    "Tech product reviews & buying guides",
    "Large/Traffic Leader",
    is_niche_authority="N", is_niche_authority_evidence="D",
    is_niche_authority_note="Site's own recorded primary_niche is broad tech product reviews & buying guides "
                             "across many categories, not a narrowly specialized sub-niche authority.",
    start_year="2007", start_year_evidence="B", start_year_url="https://en.wikipedia.org/wiki/Tom%27s_Guide",
    start_year_note="Founded 2007 by Bestofmedia, per Wikipedia; ownership chain (Bestofmedia to TechMediaNetwork 2013 to Purch 2014 to Future 2018) corroborated by Tom's Guide's own About Us page.",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", 15300000, "trailing_3_months", round(15300000/3),
        "raw_3mo_total / 3, rounded to nearest integer", "Similarweb snapshot dated ~August 2026", "B",
        "https://www.similarweb.com/website/tomsguide.com/", "traffic_scope left UNKNOWN, not independently confirmed as content-only vs. whole-domain this pass.",
    ),
    revenue_value=UNKNOWN, revenue_note="No site-specific figure found; parent Future plc reports only at company level.",
    display_ads=("UNKNOWN", UNKNOWN, UNKNOWN, "Only a ScorecardResearch tracking pixel was found on the about page, which is not itself proof of display ad units."),
    affiliate=("Y", "A", "https://www.tomsguide.com/reference/about-us", "Own about page: \"We sometimes use affiliate links to products and services on retailer sites for which we can receive compensation.\" Also discloses paid advertorials."),
    own_product=("N", "D", UNKNOWN,
                 "Business model (per its own about page's disclosed affiliate/advertorial monetization and its "
                 "recorded primary_niche as a review/buying-guide publisher) is advertising/affiliate-driven media; "
                 "no own-product offering was identified."),
    course_or_community=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    newsletter_email_capture=("Y", "A", "https://www.tomsguide.com/reference/about-us", "About page lists multiple named newsletters (Tom's Guide Daily, Tom's AI Guide, etc.)."),
))

rows.append(row(
    "toptenreviews.com", "TopTenReviews",
    "Broad consumer product/software buying guides (antivirus, VPN, home security, appliances, etc.)",
    "Large/Traffic Leader",
    is_niche_authority="N", is_niche_authority_evidence="D",
    is_niche_authority_note="Broad multi-category site.",
    is_contrast_case="N", is_contrast_case_evidence="D",
    is_contrast_case_note="Not formally flagged as contrast despite an unusually low, declining Similarweb figure (59.3K visits, -22.39% MoM) for a brand of this history -- kept as Large/Traffic Leader per its brand recognition, with the traffic anomaly flagged rather than asserted as a verified decline pattern (no independent trend data captured beyond a single snapshot).",
    start_year=UNKNOWN, start_year_note="Crunchbase founding date is redacted/obfuscated; Wikipedia entry exists but did not yield a founding year in this session's fetch.",
    traffic=traffic_block(
        "Similarweb", "total visits (most-recent-month figure)", "CONTENT_ONLY", 59300, UNKNOWN, UNKNOWN,
        "Reported as a most-recent-month figure rather than a clean 3-month total; not normalized to avoid guessing the period.",
        "Similarweb snapshot dated ~June 2026", "B",
        "https://www.similarweb.com/website/toptenreviews.com/",
        "22.39% MoM decline noted. This is a notably small number for a site of this brand recognition; flagged as worth independent cross-check (possible Similarweb subdomain/measurement quirk), reported as-shown per instructions rather than adjusted.",
    ),
    revenue_value=UNKNOWN, revenue_note="Future plc bought Purch's consumer brands (which included TopTenReviews) for ~$132M in 2018 (https://www.adexchanger.com/publishers/future-plc-plots-future-after-132m-purch-acquisition/, tier B) -- a company-bundle acquisition price, not a site-specific revenue figure.",
    display_ads=("UNKNOWN", UNKNOWN, UNKNOWN, "Not independently confirmed this pass (only a tracking pixel and newsletter form observed on homepage fetch)."),
    affiliate=("Y", "D", UNKNOWN, "Site mission language (\"helping users buy better\") plus membership in Future plc's affiliate-driven brand family; no explicit on-page disclosure text was captured this pass."),
    own_product=("N", "D", UNKNOWN,
                 "Business model (per its recorded primary_niche as a broad multi-category buying-guide publisher "
                 "and its inferred affiliate-driven monetization) is advertising/affiliate-driven media; no "
                 "own-product offering was identified."),
    course_or_community=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    newsletter_email_capture=("Y", "C", "https://www.toptenreviews.com/", "\"Sign up to our newsletter\" directly observed in site header."),
))

rows.append(row(
    "gearpatrol.com", "Gear Patrol",
    "Lifestyle/gear reviews (watches, outdoors, cars, tech, style)",
    "Mid-scale Active Site",
    is_niche_authority="N", is_niche_authority_evidence="D",
    is_niche_authority_note="Broad lifestyle/gear category.",
    is_contrast_case="N", is_contrast_case_evidence="D",
    start_year="2007", start_year_evidence="A", start_year_url="https://www.gearpatrol.com/about/about-gear-patrol/",
    start_year_note="Own About page: founded 2007 by Eric Yang and Ben Bowers.",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", 7800000, "trailing_3_months", round(7800000/3),
        "raw_3mo_total / 3, rounded to nearest integer", "Similarweb snapshot dated ~August 2026", "B",
        "https://www.similarweb.com/website/gearpatrol.com/",
        "Corroborating self-reported figures: \"over 4.8 million monthly readers\" (own About page, tier A) and founder-cited \"5.5 million unique monthly visitors\" in a Digiday interview (tier A, period unspecified, https://digiday.com/media/gear-patrol-founder-eric-yang-media-ecommerce-tech-products/) -- not reconciled with the Similarweb figure.",
    ),
    revenue_value=UNKNOWN, revenue_note="A third-party data aggregator (Kona Equity) cites \"$12.5M Revenue\" but this is an unverified estimator tool, not a disclosed/audited figure -- treated as a low-confidence lead only, not reported as fact.",
    display_ads=("UNKNOWN", UNKNOWN, UNKNOWN, "Not independently observed this pass; About page described only affiliate/store/branded content."),
    affiliate=("Y", "A", "https://www.gearpatrol.com/about/about-gear-patrol/", "About page: \"Gear Patrol links to featured products via Amazon and other online retailers... may earn a small percentage of the purchase price as a referral fee.\" Founder also states in a Digiday interview they hold \"one of the first Amazon Associates accounts.\""),
    own_product=("Y", "A", "https://www.gearpatrol.com/about/about-gear-patrol/", "Operates the \"Gear Patrol Store\" selling own merchandise."),
    course_or_community=("UNKNOWN", UNKNOWN, UNKNOWN, "No evidence found."),
    newsletter_email_capture=("UNKNOWN", UNKNOWN, UNKNOWN, "Not directly observed this pass."),
))

rows.append(row(
    "vacuumwars.com", "Vacuum Wars",
    "Robot/vacuum cleaner reviews",
    "Mid-scale Active Site",
    is_niche_authority="Y", is_niche_authority_evidence="D",
    is_niche_authority_note="CEO Christopher White is described as holding \"one of the largest private collections\" of robot vacuums with a 300K+ subscriber YouTube channel; combined with dedicated single-category focus, reads as a leading authority for the robot-vacuum sub-niche, though no third-party \"definitive site\" statement was found to support tier A/B.",
    is_contrast_case="N", is_contrast_case_evidence="D",
    start_year="2017", start_year_evidence="A", start_year_url="https://vacuumwars.com/about/",
    start_year_note="Own about page states 2017.",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", 672600, "trailing_3_months", round(672600/3),
        "raw_3mo_total / 3, rounded to nearest integer", "Similarweb snapshot dated ~July 2026", "B",
        "https://vacuumwars.com/about/",
        "Corroborating third-party marketing case study claims \"1,046% traffic growth in 3 months\" (https://aioseo.com/trends/vacuum-wars-seo-case-study/, tier B) -- supports an active-growth trajectory rather than decline.",
    ),
    revenue_value=UNKNOWN, revenue_note="No disclosed figures found.",
    display_ads=("UNKNOWN", UNKNOWN, UNKNOWN, "About page did not mention display ads, only affiliate program participation."),
    affiliate=("Y", "A", "https://vacuumwars.com/about/", "About page: participates in \"Amazon Services LLC Associates Program as well as the Walmart affiliate program and others.\""),
    own_product=("N", "A", "https://vacuumwars.com/about/", "About page explicitly states no sponsorships/free products accepted since 2020; no own-product line found."),
    course_or_community=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    newsletter_email_capture=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
))

rows.append(row(
    "runrepeat.com", "RunRepeat",
    "Running shoe reviews (lab + wear-testing)",
    "Narrow Niche Authority",
    is_niche_authority="Y", is_niche_authority_evidence="B", is_niche_authority_url="https://runrepeat.com/about",
    is_niche_authority_note="Widely cited running-shoe review methodology (\"buy all shoes with our own money... cut all shoes in half\", 30+ metrics per shoe) is a recognized reference point in the running-shoe review space, corroborated by dedicated Similarweb comparison pages against Runner's World and Doctors of Running as direct competitors in the same narrow niche.",
    is_contrast_case="N", is_contrast_case_evidence="D",
    start_year=UNKNOWN, start_year_note="About page and search results did not surface an explicit founding year for founder Jens Jakob Andersen's site (RunRepeat ApS, Denmark).",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", 7600000, "trailing_3_months", round(7600000/3),
        "raw_3mo_total / 3, rounded to nearest integer", "Similarweb snapshot dated ~July 2026", "B",
        "https://www.similarweb.com/website/runrepeat.com/", "",
    ),
    revenue_value=UNKNOWN, revenue_note="No disclosed figures found.",
    display_ads=("Y", "A", "https://runrepeat.com/about", "About page: \"We also have ads to support our operations.\""),
    affiliate=("Y", "A", "https://runrepeat.com/about", "About page: \"If you click through to the retailer and you buy the shoe, we get an affiliate commission on the sale\"; also states Amazon Associates membership."),
    own_product=("N", "D", UNKNOWN,
                 "Business model (per its own about page's disclosed ad/affiliate monetization and its recorded "
                 "primary_niche as a review/wear-testing publisher) is advertising/affiliate-driven media; no "
                 "own-product offering was identified."),
    course_or_community=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    newsletter_email_capture=("UNKNOWN", UNKNOWN, UNKNOWN, "Not observed this pass."),
))

rows.append(row(
    "babygearlab.com", "BabyGearLab",
    "Baby gear/products reviews (car seats, strollers, carriers, etc.)",
    "Narrow Niche Authority",
    is_niche_authority="Y", is_niche_authority_evidence="A", is_niche_authority_url="https://www.babygearlab.com/about",
    is_niche_authority_note="Founder Dr. Juliet Spurrier (board-certified pediatrician) is described on the site's own About page as personally overseeing all reviews; site brands itself \"Home of the World's Best Baby Product Reviews\" and is a commonly cited reference for car-seat/stroller/carrier buying guides.",
    is_contrast_case="N", is_contrast_case_evidence="D",
    start_year="2013", start_year_evidence="C", start_year_url="http://www.prweb.com/releases/2013/2/prweb10485911.htm",
    start_year_note="Earliest verifiable activity found is a Feb 2013 PRWeb press release (\"BabyGearLab.com Announces 2013 Best Baby Carrier Review Awards\"), used as a floor/lower-bound rather than a confirmed founding date.",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", 451900, "trailing_3_months", round(451900/3),
        "raw_3mo_total / 3, rounded to nearest integer", "Similarweb snapshot dated ~May 2026", "B",
        "https://www.similarweb.com/website/babygearlab.com/", "",
    ),
    revenue_value=UNKNOWN, revenue_note="No disclosed figures found.",
    display_ads=("N", "A", "https://www.babygearlab.com/about", "Own About page explicitly states the site \"remains ad-free\", monetizing only via affiliate commissions."),
    affiliate=("Y", "A", "https://www.babygearlab.com/about", "\"We only make money when you click on our affiliate links and buy products we've reviewed.\""),
    own_product=("N", "A", "https://www.babygearlab.com/about", "About page confirms they purchase all products at retail and don't sell their own."),
    course_or_community=("UNKNOWN", UNKNOWN, UNKNOWN, "No evidence found."),
    newsletter_email_capture=("UNKNOWN", UNKNOWN, UNKNOWN, "Not directly observed this pass."),
))

rows.append(row(
    "homegrounds.co", "Home Grounds",
    "Home coffee brewing equipment & bean reviews (espresso machines, grinders, brewers)",
    "Narrow Niche Authority",
    is_niche_authority="Y", is_niche_authority_evidence="B", is_niche_authority_url="https://www.homegrounds.co/about/",
    is_niche_authority_note="Single-category focus (home coffee brewing/equipment) since 2015, SCA (Specialty Coffee Association) membership claimed, dedicated editorial team, and a large single-topic social following (Facebook 86.9K, YouTube 21.8K). Authority claims (e.g. \"world's largest home barista community\") are the operator's own marketing language, not independently verified by a third party.",
    is_contrast_case="N", is_contrast_case_evidence="D",
    start_year="2015", start_year_evidence="B", start_year_url="https://www.blexr.com/brewing-up-success-with-home-grounds-coffee-site/",
    start_year_note="Acquirer Blexr's own acquisition writeup states 2015, corroborated by the site's own About page.",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", 56800, "trailing_3_months", UNKNOWN,
        "Similarweb's free public page did not expose a clean monthly-average figure without login; reporting the raw 3-month total as shown rather than inferring a monthly split.",
        "Similarweb snapshot dated August 2026", "C",
        "https://www.similarweb.com/website/homegrounds.co/",
        "Owner (Blexr) separately claims \"millions of visitors each year\" (unquantified, tier B, https://www.blexr.com/brewing-up-success-with-home-grounds-coffee-site/) -- directionally much higher than this Similarweb estimate; both reported as approximate and non-reconciled.",
    ),
    revenue_value=UNKNOWN, revenue_note="Blexr disclosed \"a six-figure sum\" as the 2021 acquisition price (tier B, same source), not ongoing revenue -- a purchase price, not a revenue figure, so revenue itself is UNKNOWN.",
    display_ads=("UNKNOWN", UNKNOWN, UNKNOWN, "No display/banner ad network observed on the sampled page, but this could reflect ad-blocking/rendering in the fetch rather than true absence."),
    affiliate=("Y", "C", "https://www.homegrounds.co/best-ground-coffee/", "\"SEE ON AMAZON\" buttons, geni.us affiliate links, and an explicit disclosure: \"Homegrounds is reader-supported. When you buy via the links on our site, we may earn an affiliate commission at no cost to you.\""),
    own_product=("N", "C", "https://www.homegrounds.co/about/", "Described as a review/affiliate site with no direct product line; reviews third-party coffee equipment and beans."),
    course_or_community=("Y", "C", "https://www.homegrounds.co/about/", "Describes itself as \"the world's largest home barista community\" and runs an 86.9K-member Facebook group. No paid course found; course specifically is UNKNOWN, community is Y."),
    newsletter_email_capture=("Y", "C", "https://www.homegrounds.co/about/", "Email subscribe field/button visible in site navigation."),
))

rows.append(row(
    "the-gadgeteer.com", "The Gadgeteer",
    "General gadget/tech product reviews",
    "Contrast Cohort",
    is_niche_authority="N", is_niche_authority_evidence="D",
    is_niche_authority_note="Broad gadget category, not a single narrow product type.",
    is_contrast_case="Y", is_contrast_case_evidence="B", is_contrast_case_url="https://www.similarweb.com/website/the-gadgeteer.com/",
    is_contrast_case_note="28+ years of continuous operation (1997-2025, self-stated in the site's own 25th-anniversary post) with over 24,000 news/review posts, yet current Similarweb global rank is only #64,011 with ~367K monthly visits and a recent 12.5% MoM decline -- modest traffic for a site of this operating age and content volume compared to peers like PCMag/Tom's Guide. Ownership was transferred in Dec 2025 (founder stepping back after 28 years), which the new owners explicitly frame as NOT a cadence drop (\"Nothing... It is continuing on just the way it always has\"), so only the low_traction_despite_age pattern is asserted, not cadence_drop.",
    contrast_pattern="low_traction_despite_age", contrast_evidence_period="28+ years operating (1997-2025) vs. current ~367K/mo traffic and #64,011 global rank, with a 12.5% MoM decline observed at Similarweb lookup 2026-09-17.",
    start_year="1997", start_year_evidence="A", start_year_url="https://the-gadgeteer.com/2022/09/16/the-gadgeteer-is-25-years-old-have-you-been-here-from-the-start/",
    start_year_note="Founder Julie Strietelmeier's own account: started on USENET/Geocities, then bought the-gadgeteer.com domain in Dec 1997.",
    traffic=traffic_block(
        "Similarweb", "total visits", "CONTENT_ONLY", 1100000, "trailing_3_months", round(1100000/3),
        "raw_3mo_total / 3, rounded to nearest integer", "Similarweb snapshot dated ~August 2026", "B",
        "https://www.similarweb.com/website/the-gadgeteer.com/",
        "Global rank #64,011, category rank #132 US Consumer Electronics, 12.5% MoM decrease noted.",
    ),
    revenue_value=UNKNOWN, revenue_note="No disclosed figures found.",
    display_ads=("Y", "A", "https://the-gadgeteer.com/disclosure/", "Own Disclosure page: \"accepts forms of cash advertising, sponsorship, paid insertions, affiliate links, or other forms of compensation.\""),
    affiliate=("Y", "A", "https://the-gadgeteer.com/disclosure/", "Same disclosure page: participant in \"Amazon Services LLC Associates Program, Sharesale, Commission Junction, Impact Radius, Avantlinks, and Skimlinks.\""),
    own_product=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    course_or_community=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    newsletter_email_capture=("Y", "C", "https://the-gadgeteer.com/", "Site navigation includes a \"Follow Us!\" link to a dedicated /subscribe/ page."),
))

rows.append(row(
    "consumersearch.com", "ConsumerSearch (historical)",
    "Meta-review aggregator (compiled/synthesized reviews across ~250 product categories)",
    "Contrast Cohort",
    is_niche_authority="N", is_niche_authority_evidence="D",
    is_niche_authority_note="Site's own recorded primary_niche is a meta-review aggregator spanning ~250 broad "
                             "product categories, not a narrow niche authority, and the domain no longer functions "
                             "as a review site at all (contrast_pattern=shutdown).",
    is_contrast_case="Y", is_contrast_case_evidence="C", is_contrast_case_url="https://consumersearch.com/",
    is_contrast_case_note="Fetching consumersearch.com live on 2026-09-17 returned not a review site but an unrelated farewell/memorial page for Ask.com (\"After 30 years of answering the world's questions, Ask.com officially closed on May 1, 2026\"), indicating the domain has been repurposed/consolidated by its current corporate owner (IAC) and the original ConsumerSearch review-site brand no longer resolves at this URL at all. The exact year ConsumerSearch itself stopped publishing new reviews is UNKNOWN and not asserted.",
    contrast_pattern="shutdown", contrast_evidence_period="Acquired by About.com/New York Times Co. in 2007; domain now resolves to an unrelated Ask.com closure notice as observed 2026-09-17.",
    start_year=UNKNOWN, start_year_note="Not found in sources retrieved this pass; site already an established meta-review publisher by 2007 when acquired.",
    traffic=None,
    revenue_value=UNKNOWN, revenue_figure_period="2007-05-07 acquisition announcement",
    revenue_note="About.com (New York Times Co.) acquired ConsumerSearch.com for $33 million, announced 2007-05-07 (https://www.rttnews.com/295951/new-york-times-about-com-acquires-consumersearch-com-for-33-mln-quick-facts.aspx, tier B). This is an acquisition price, not ongoing revenue. [pre-950 hardening] revenue_value normalized to UNKNOWN per the Study A revenue-field policy: an acquisition/purchase price is not a revenue figure and must never populate revenue_value -- it is preserved here in revenue_note only.",
    display_ads=("UNKNOWN", UNKNOWN, UNKNOWN, "Not applicable -- site no longer functions as a review site."),
    affiliate=("UNKNOWN", UNKNOWN, UNKNOWN, "Historical; not verifiable now that the domain no longer serves review content."),
    own_product=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    course_or_community=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
    newsletter_email_capture=("UNKNOWN", UNKNOWN, UNKNOWN, ""),
))

print(f"Category 4 (Product Review/Buying Guides) rows so far: {len(rows)}")
assert len(rows) == 40, f"Expected 40 rows, got {len(rows)}"

domains = [r["canonical_root_domain"] for r in rows]
assert len(domains) == len(set(domains)), f"Duplicate domains within the 40: {[d for d in domains if domains.count(d) > 1]}"

# schema_extend must run BEFORE evidence_harden.harden_rows() now: since the
# last pre-950 patch, content_scale_proxy is part of evidence_harden.ALL_GROUPS,
# so harden_row() needs those fields to already exist on each row dict --
# they are only added here, in bulk, not by the individual row() calls above.
schema_extend.extend_rows_with_production_schema(rows, start_index=10)

rows = evidence_harden.harden_rows(rows)
print("Applied evidence_harden.harden_rows() (pre-950 hardening pass) to all 40 new rows.")

with open(OUT_40, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=FIELDNAMES)
    w.writeheader()
    for r in rows:
        w.writerow({k: r[k] for k in FIELDNAMES})
print(f"Wrote {len(rows)} rows to {OUT_40}")

# ---- Concatenate with the existing 10 A0-Phase1 rows into a 50-row cumulative dataset ----
with EXISTING_10.open(newline="", encoding="utf-8") as f:
    existing_10_rows = list(csv.DictReader(f))
assert len(existing_10_rows) == 10, f"Expected 10 existing rows, got {len(existing_10_rows)}"

all_50 = existing_10_rows + rows
all_domains = [r["canonical_root_domain"] for r in all_50]
assert len(all_domains) == len(set(all_domains)), f"Duplicate domains across the full 50: {[d for d in all_domains if all_domains.count(d) > 1]}"
assert len(all_50) == 50

with open(OUT_50, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=FIELDNAMES)
    w.writeheader()
    for r in all_50:
        w.writerow({k: r[k] for k in FIELDNAMES})
print(f"Wrote {len(all_50)} rows to {OUT_50}")
