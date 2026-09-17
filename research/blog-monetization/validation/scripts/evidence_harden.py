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

Last pre-950 engineering patch (2026-09-17, commit 8dffb08 GPT follow-up,
Item 1): `content_scale_proxy` is a production-schema evidence-bearing
group (schema_extend.py) that was added to the canonical CSV columns but
was NOT included in ALL_GROUPS below, so it was silently skipped by every
consumer of ALL_GROUPS (evidence_harden's own consistency checks,
summarize_dataset.py's UNKNOWN-rate / completion-rate / evidence-tier
sections). It is now included in ALL_GROUPS (as CONTENT_SCALE_PROXY_GROUP),
plus one extra rule specific to its 5th field (`_method`, which none of
the other groups have): `content_scale_proxy_value != UNKNOWN` requires
`content_scale_proxy_method != UNKNOWN` too (you can't have a scale
number without knowing what produced it).

Also new this round: `verify_group_coverage(fieldnames)` -- a structural
check that every `*_evidence` column actually present in a schema's field
list belongs to EXACTLY one group in ALL_GROUPS (Item 1's explicit ask:
"모든 *_evidence 컬럼이 정확히 하나의 evidence group에 속하는지 검사.
누락/중복이면 FAIL"). This is what makes a future repeat of "a new
evidence-bearing field was added to the schema but never wired into
ALL_GROUPS" a loud, machine-detectable Gate failure instead of a silent
under-count.
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

# content_scale_proxy has a 5th field (_method) with no equivalent in any
# other group, so it is validated with the standard 4-tuple ALL_GROUPS
# machinery (below) PLUS one extra rule in harden_row() for _method.
CONTENT_SCALE_PROXY_GROUP = [
    ("content_scale_proxy_value", "content_scale_proxy_evidence", "content_scale_proxy_source_url", "content_scale_proxy_note"),
]

ALL_GROUPS = SIMPLE_GROUPS + COMPOSITE_GROUPS + CONTENT_SCALE_PROXY_GROUP


class EvidenceHardenError(ValueError):
    pass


def verify_group_coverage(fieldnames) -> tuple:
    """
    Structural coverage check (Item 1, last pre-950 patch): every
    `*_evidence` column in `fieldnames` must belong to EXACTLY one group
    in ALL_GROUPS -- no evidence-bearing field silently missing from
    ALL_GROUPS (as content_scale_proxy previously was), and no field
    listed twice. Returns (missing, duplicated) -- both empty on success.
    """
    schema_evidence_fields = [f for f in fieldnames if f.endswith("_evidence")]
    group_evidence_fields = [g[1] for g in ALL_GROUPS]
    from collections import Counter
    counts = Counter(group_evidence_fields)
    missing = sorted(set(schema_evidence_fields) - set(group_evidence_fields))
    duplicated = sorted(f for f, c in counts.items() if c > 1)
    return missing, duplicated


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

    # content_scale_proxy-specific rule (Item 1, last pre-950 patch): a
    # non-UNKNOWN proxy value must always carry a non-UNKNOWN method --
    # you can't report a content-scale number without knowing what
    # produced it (sitemap count, index count, etc.).
    proxy_value = str(d.get("content_scale_proxy_value", "UNKNOWN")).strip()
    proxy_method = str(d.get("content_scale_proxy_method", "UNKNOWN")).strip()
    if proxy_value != "UNKNOWN" and proxy_method == "UNKNOWN":
        raise EvidenceHardenError(
            f"{domain}: content_scale_proxy_value={proxy_value!r} but content_scale_proxy_method=UNKNOWN -- "
            f"a non-UNKNOWN proxy value must state the method that produced it."
        )

    return d


def harden_rows(rows: list) -> list:
    return [harden_row(r) for r in rows]
