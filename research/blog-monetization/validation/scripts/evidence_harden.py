#!/usr/bin/env python3
"""
Shared post-processing pass applied to every generated row (both
migrate_schema.py's 10 A0-Phase1 rows and build_a0_phase2.py's 40
A0-Phase2 rows) to enforce the evidence-semantics rules confirmed during
the pre-950 hardening round (2026-09-17):

  1. Rule #8 (unchanged): value == UNKNOWN  =>  evidence must be UNKNOWN.
  2. New: value != UNKNOWN  =>  evidence must NOT be UNKNOWN. A value can
     never be asserted (Y/N, a number, a year) without SOME evidence tier
     backing it. If this is violated the row must be fixed by hand in the
     generator script -- this module refuses to guess a tier, it only
     raises so the inconsistency surfaces immediately during generation.
  3. New: evidence in (A, B, C)  =>  the field's DEDICATED source_url must
     be a real http(s) URL (no note-text fallback -- unchanged principle
     from the earlier hardening round, now applied to C as well as A/B).
     For evidence == C specifically (the researcher's own direct site
     observation), if no URL was captured in the original research pass,
     this module backfills the site's own homepage ("https://{domain}/")
     as the source_url -- this is not a new claim or new research, it is
     simply naming the page a C-tier "I looked at the site" observation
     is inherently about. A/B evidence lacking a URL is NOT auto-filled
     (that would require inventing a citation) -- it raises instead, so
     the generator script must supply a real URL or downgrade the tier.
  4. New: evidence == D  =>  note must be non-empty (the reasoning behind
     a D-tier inference must always be stated in the note, never left
     blank). If a generator forgot to pass a note, this module fills a
     transparent placeholder rather than fabricating a reason.

This module performs NO web research and invents NO facts. It only
(a) verifies internal consistency of data already supplied by the
generator scripts, and (b) backfills two specific, clearly-labeled,
mechanical defaults (a C-tier homepage URL; a D-tier placeholder note)
that were already implied by the evidence tier itself.
"""

# (value_field, evidence_field, source_url_field, note_field) for every
# evidence-bearing group in the Protocol V2 canonical schema.
SIMPLE_GROUPS = [
    ("is_niche_authority", "is_niche_authority_evidence", "is_niche_authority_source_url", "is_niche_authority_note"),
    ("is_contrast_case", "is_contrast_case_evidence", "is_contrast_case_source_url", "is_contrast_case_note"),
    ("display_ads", "display_ads_evidence", "display_ads_source_url", "display_ads_note"),
    ("affiliate", "affiliate_evidence", "affiliate_source_url", "affiliate_note"),
    ("own_product", "own_product_evidence", "own_product_source_url", "own_product_note"),
    ("course_or_community", "course_or_community_evidence", "course_or_community_source_url", "course_or_community_note"),
    ("newsletter_email_capture", "newsletter_email_capture_evidence", "newsletter_email_capture_source_url", "newsletter_email_capture_note"),
]

COMPOSITE_GROUPS = [
    ("start_year_value", "start_year_evidence", "start_year_source_url", "start_year_note"),
    ("traffic_value_raw", "traffic_evidence", "traffic_source_url", "traffic_note"),
    ("revenue_value", "revenue_evidence", "revenue_source_url", "revenue_note"),
]

ALL_GROUPS = SIMPLE_GROUPS + COMPOSITE_GROUPS

D_TIER_PLACEHOLDER_NOTE = (
    "D-tier inference; no additional reasoning was captured for this field during the "
    "original research pass, and no new research was performed to add one during this "
    "hardening round -- left as a plain, undetailed reasoned inference."
)


class EvidenceHardenError(ValueError):
    pass


def harden_row(d: dict) -> dict:
    domain = d["canonical_root_domain"]
    homepage = f"https://{domain}/"

    for value_field, ev_field, url_field, note_field in ALL_GROUPS:
        value = str(d[value_field]).strip()
        ev = str(d[ev_field]).strip()
        url = str(d[url_field]).strip()
        note = str(d[note_field]).strip()

        if value == "UNKNOWN":
            # Rule #8: UNKNOWN value always carries UNKNOWN evidence.
            if ev != "UNKNOWN":
                d[ev_field] = "UNKNOWN"
            continue

        # value is asserted (not UNKNOWN) -> evidence must be asserted too.
        if ev == "UNKNOWN":
            raise EvidenceHardenError(
                f"{domain}: {value_field}={value!r} but {ev_field}=UNKNOWN -- "
                f"a non-UNKNOWN value must carry a real evidence tier. Fix in the generator script."
            )

        if ev in ("A", "B", "C"):
            has_valid_url = url.lower().startswith(("http://", "https://"))
            if not has_valid_url:
                if ev == "C":
                    d[url_field] = homepage
                    if "source_url backfilled to site homepage" not in note:
                        d[note_field] = (note + " [source_url backfilled to site homepage during pre-950 "
                                          "hardening pass -- same observation already described in this note, "
                                          "no new claim or new research.]").strip()
                else:
                    raise EvidenceHardenError(
                        f"{domain}: {value_field} has evidence={ev} but no valid dedicated {url_field} "
                        f"-- A/B evidence must cite a real URL; fix in the generator script "
                        f"(supply the URL or downgrade the tier)."
                    )

        if ev == "D" and not note:
            d[note_field] = D_TIER_PLACEHOLDER_NOTE

    return d


def harden_rows(rows: list) -> list:
    return [harden_row(r) for r in rows]
