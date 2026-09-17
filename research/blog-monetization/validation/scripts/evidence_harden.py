#!/usr/bin/env python3
"""
Shared post-processing pass applied to every generated row (both
migrate_schema.py's 10 A0-Phase1 rows and build_a0_phase2.py's 40
A0-Phase2 rows) to enforce the evidence-semantics rules confirmed during
the pre-950 hardening round (2026-09-17), STRICT VARIANT confirmed during
the follow-up "remove auto-fabrication" engineering patch (2026-09-17,
same day, GPT-reviewed commit 8dffb08 follow-up):

  1. Rule #8 (unchanged): value == UNKNOWN  =>  evidence must be UNKNOWN.
  2. value != UNKNOWN  =>  evidence must NOT be UNKNOWN. A value can never
     be asserted (Y/N, a number, a year) without SOME evidence tier
     backing it. Raises so the generator script must fix it by hand.
  3. evidence in (A, B, C)  =>  the field's DEDICATED source_url must be a
     real http(s) URL (no note-text fallback). This module does NOT
     auto-backfill anything, for ANY tier including C -- a prior version
     of this module auto-filled a guessed site-homepage URL for C-tier
     evidence lacking one; that guess could be wrong (the actual
     observation might have been a sub-page, a search result, or a
     different property entirely) and is a form of fabrication. This
     version raises EvidenceHardenError instead. The generator script
     must supply the real URL actually used, or downgrade the tier if it
     isn't known.
  4. evidence == D  =>  note must be non-empty. This module does NOT
     auto-fill a generic placeholder note -- a prior version did, which
     is a form of fabricated (contentless) reasoning. This version raises
     EvidenceHardenError instead. The generator script must supply the
     real reasoning that justified the D-tier inference.

This module performs NO web research and invents NO facts, NO URLs, and
NO reasoning text. It is purely a consistency CHECK now -- every value it
writes into a row (other than forcing evidence=UNKNOWN under Rule #8) is
supplied by the caller before harden_row() is invoked, typically via an
explicit, human-reviewed correction table in the generator script (see
migrate_schema.py's KNOWN_C_TIER_HOMEPAGE_CITATIONS /
KNOWN_REVERT_TO_UNKNOWN and build_a0_phase2.py's
KNOWN_D_TIER_REASONING_NOTES for the pre-950 dataset's specific
corrections, each individually reviewed against the original research
notes rather than applied as a blanket rule).
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


class EvidenceHardenError(ValueError):
    pass


def harden_row(d: dict) -> dict:
    domain = d["canonical_root_domain"]

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
                raise EvidenceHardenError(
                    f"{domain}: {value_field} has evidence={ev} but no valid dedicated {url_field} "
                    f"-- A/B/C evidence must cite a real URL (no auto-backfill); fix in the generator "
                    f"script by supplying the URL actually used or downgrading the tier."
                )

        if ev == "D" and not note:
            raise EvidenceHardenError(
                f"{domain}: {value_field} has evidence=D but {note_field} is empty -- "
                f"D-tier inference must always state its real reasoning (no placeholder auto-fill); "
                f"fix in the generator script."
            )

    return d


def harden_rows(rows: list) -> list:
    return [harden_row(r) for r in rows]
