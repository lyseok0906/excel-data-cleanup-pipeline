#!/usr/bin/env python3
"""
Adds the Study A production-schema fields that Protocol V2 Section 2 has
always specified but that never actually made it into validation_10_v2.csv /
validation_50_v2.csv's canonical schema (GPT-reviewed follow-up to commit
8dffb08, 2026-09-17):

    category                 -- fixed enum (CATEGORY_ENUM below), separate
                                 from the free-text `primary_niche` field.
    sub_category              -- reserved for future finer-grained
                                 taxonomy; left UNKNOWN for the current 50
                                 (no sub-category-level research exists).
    as_of_date                -- ISO date the row's research was current
                                 as of, at the batch level (already known
                                 from when each batch was executed -- not
                                 new research).
    content_scale_proxy_value/_method/_evidence/_source_url/_note
                              -- a 5-field evidence-bearing group (same
                                 value/evidence/source_url/note pattern as
                                 every other Section 3 field) for an
                                 automatable content-scale proxy (e.g.
                                 sitemap/index-count). No such proxy was
                                 collected during A0-Phase1/Phase2, so this
                                 is UNKNOWN for all 50 current rows -- this
                                 round adds the FIELD, not new data.

This module does NOT perform new web research. `category` is assigned
purely from already-known batch design (A0-Phase1 was the 10-site
Productivity/PKM batch; A0-Phase2 was four 10-site batches in a fixed,
already-documented order -- see CATEGORY_BATCH_PLAN below, which mirrors
migrate_schema.py's row order and build_a0_phase2.py's own "Category N
(...)" print statements) plus DOMAIN_CATEGORY_OVERRIDES for the one batch
that needed a within-batch split (see Section 3 below).

Last pre-950 engineering patch (2026-09-17, commit 8dffb08 GPT follow-up,
Item 3 -- "production category taxonomy 확정"): the original 5-value
CATEGORY_ENUM only covered the categories A0 had actually executed, not
the full 1000-site Study A taxonomy. This round confirms the FINAL
production taxonomy (11 values) so the enum does not need to change again
mid-950-expansion, using two already-known sources and NO new research:

  1. The original 100-site pilot study (pilot-100/sites.csv) already ran
     a 10-category broad-market design: Career/Education,
     Excel/Spreadsheet/Productivity, Food/Recipe, Gardening/Outdoor,
     Home/DIY, Other Strong Niche, Personal Finance,
     Product Review/Buying Guides, Software/Tech Tutorials, Travel.
  2. A0-Phase1's 10-site Productivity/PKM batch demonstrated that
     "Productivity/PKM" tools (Notion/PKM-adjacent blogs) are
     meaningfully distinct from "Excel/Spreadsheet" tools even though the
     pilot study's single "Excel/Spreadsheet/Productivity" bucket lumped
     them together -- A0 already sampled them as two separate 10-site
     batches, so the production taxonomy keeps that split rather than
     re-merging it.

  Decision: production CATEGORY_ENUM = the pilot's 10 categories, with
  "Excel/Spreadsheet/Productivity" split into "Productivity / PKM" and
  "Excel / Spreadsheet" (net 11 categories), and "Home/DIY" further kept
  distinct from "Food/Recipe" (the pilot already treated these as two
  separate categories; A0-Phase2's "Home / DIY & Food" batch had merged
  them for convenience only -- this round un-merges that batch's 10 rows
  using each row's ALREADY-RECORDED primary_niche, see
  DOMAIN_CATEGORY_OVERRIDES, no new research performed).

  The pilot's own "Excel/Spreadsheet/Productivity" 10 rows are NOT
  force-split into Productivity/PKM vs. Excel/Spreadsheet here, because
  doing so correctly would require inspecting each of those 10 sites
  individually -- new research, which this round does not do. Those rows
  keep an explicit pass-through legacy label instead (see
  PRIOR_PILOT_CATEGORY_MAP below); they are EXCLUDED_PRIOR_PILOT registry
  rows, never part of the actual Study A dataset, so this does not affect
  CATEGORY_ENUM validation of validation_50_v2.csv.
"""

from datetime import date

# Fixed PRODUCTION category taxonomy for the full 1000-site Study A
# (Protocol V2 Section 2 / Section 7-D Item 3, finalized in the last
# pre-950 engineering patch so the enum will not need to change again
# mid-950-expansion). This is deliberately a CLOSED enum, not free text --
# primary_niche remains the free-text detail field. New categories are
# added here only when a new batch's category is actually decided (never
# inferred implicitly at CSV-write time).
CATEGORY_ENUM = [
    "Productivity / PKM",
    "Excel / Spreadsheet",
    "Personal Finance",
    "Home / DIY",
    "Food / Recipe",
    "Product Review / Buying Guides",
    "Career / Education",
    "Gardening / Outdoor",
    "Software / Tech Tutorials",
    "Travel",
    "Other Strong Niche",
]

# Explicit mapping from the original 100-site pilot study's own `category`
# column values (pilot-100/sites.csv) to the production taxonomy above --
# used ONLY for EXCLUDED_PRIOR_PILOT registry rows (build_domain_registry.py),
# never for the actual Study A dataset. Every pilot category maps 1:1 to a
# production CATEGORY_ENUM value EXCEPT "Excel/Spreadsheet/Productivity",
# which pilot-100 never split into Productivity/PKM vs. Excel/Spreadsheet
# (doing so would require inspecting each of those 10 sites individually --
# new research, not performed this round). That one legacy bucket keeps an
# explicit, clearly-labeled pass-through value instead of being forced into
# either half of the production enum or silently left as pilot's raw string.
PRIOR_PILOT_CATEGORY_MAP = {
    "Career/Education": "Career / Education",
    "Excel/Spreadsheet/Productivity": "Excel/Spreadsheet/Productivity (pilot-100 legacy bucket -- not split into Productivity/PKM vs. Excel/Spreadsheet without new research)",
    "Food/Recipe": "Food / Recipe",
    "Gardening/Outdoor": "Gardening / Outdoor",
    "Home/DIY": "Home / DIY",
    "Other Strong Niche": "Other Strong Niche",
    "Personal Finance": "Personal Finance",
    "Product Review/Buying Guides": "Product Review / Buying Guides",
    "Software/Tech Tutorials": "Software / Tech Tutorials",
    "Travel": "Travel",
}

# Per-domain category overrides, applied AFTER the batch-level default
# below (Section 3-6 / Item 3 of the last pre-950 patch): A0-Phase2's
# "Home / DIY & Food" batch (10 sites) is un-merged into "Home / DIY" (5)
# and "Food / Recipe" (5) using each site's ALREADY-RECORDED primary_niche
# in validation_50_v2.csv -- no new research. This is a clean 5/5 split:
# food/recipe/baking sites vs. home-decor/DIY/woodworking/tiny-house sites.
DOMAIN_CATEGORY_OVERRIDES = {
    # Food / Recipe (primary_niche already recorded as food/recipe/baking content)
    "seriouseats.com": "Food / Recipe",           # "Food journalism/recipes/food science"
    "101cookbooks.com": "Food / Recipe",          # "Vegetarian/whole-foods recipes"
    "loveandlemons.com": "Food / Recipe",         # "Vegetarian recipes"
    "theperfectloaf.com": "Food / Recipe",        # "Sourdough baking (technique/science)"
    "afarmgirlsdabbles.com": "Food / Recipe",     # "Home-cooking/family recipes"
    # Home / DIY (primary_niche already recorded as home-decor/DIY/woodworking content)
    "apartmenttherapy.com": "Home / DIY",         # "Home decor/organization media"
    "designsponge.com": "Home / DIY",             # "Interior design/DIY blog (defunct)"
    "shanty-2-chic.com": "Home / DIY",            # "DIY furniture building plans"
    "tinyhousetalk.com": "Home / DIY",            # "Tiny house movement (curation/news)"
    "thewoodwhisperer.com": "Home / DIY",         # "Woodworking instruction/video"
}

# Ordered list of (default_category, as_of_date, row_count) describing
# exactly how the current 50-row Study A cumulative dataset was assembled,
# in row order (this mirrors migrate_schema.py's FIELDNAMES row order
# followed by build_a0_phase2.py's four batches of 10, each already fixed
# and documented in research_protocol_v2.md Section 7-A/7-B/7-D and
# A0_Phase2_report.md -- not a new decision made by this module). The
# batch-3 default of "Home / DIY" below is a placeholder only -- every one
# of its 10 rows is overridden by DOMAIN_CATEGORY_OVERRIDES above (5 to
# "Food / Recipe", 5 stay "Home / DIY"), kept as a valid CATEGORY_ENUM
# member purely as a fail-safe in case a future row in that batch position
# were ever added without an explicit override.
CATEGORY_BATCH_PLAN = [
    ("Productivity / PKM", "2026-09-16", 10),               # A0-Phase1
    ("Excel / Spreadsheet", "2026-09-17", 10),               # A0-Phase2 batch 1
    ("Personal Finance", "2026-09-17", 10),                  # A0-Phase2 batch 2
    ("Home / DIY", "2026-09-17", 10),                        # A0-Phase2 batch 3 (split via DOMAIN_CATEGORY_OVERRIDES)
    ("Product Review / Buying Guides", "2026-09-17", 10),    # A0-Phase2 batch 4
]

# category/sub_category/as_of_date are placed near primary_niche in each
# generator script's own FIELDNAMES list (not part of this constant) for
# readability; this constant covers only the content_scale_proxy group,
# which is appended at the end of the schema like every other new group
# added in past hardening rounds.
EXTRA_FIELDNAMES = [
    "content_scale_proxy_value",
    "content_scale_proxy_method",
    "content_scale_proxy_evidence",
    "content_scale_proxy_source_url",
    "content_scale_proxy_note",
]

ALL_NEW_FIELDNAMES = ["category", "sub_category", "as_of_date"] + EXTRA_FIELDNAMES

_NO_PROXY_NOTE = (
    "No sitemap/index-count (or other automatable) content-scale proxy was "
    "collected during A0-Phase1/A0-Phase2 research -- this field was added "
    "to the production schema in this round without new research, per "
    "instruction to leave it UNKNOWN rather than backfill a guessed value."
)


def category_sequence_for(n_rows: int):
    """
    Yield (category, as_of_date) for each of the first n_rows rows, in
    CATEGORY_BATCH_PLAN order. Raises if n_rows exceeds the plan's total
    (keeps this from silently mis-tagging rows if the dataset grows before
    the plan is updated).
    """
    total_planned = sum(c for _, _, c in CATEGORY_BATCH_PLAN)
    if n_rows > total_planned:
        raise ValueError(
            f"category_sequence_for({n_rows}) exceeds CATEGORY_BATCH_PLAN's "
            f"total of {total_planned} rows -- update CATEGORY_BATCH_PLAN first."
        )
    out = []
    for category, as_of, count in CATEGORY_BATCH_PLAN:
        take = min(count, n_rows - len(out))
        out.extend([(category, as_of)] * take)
        if len(out) >= n_rows:
            break
    return out


def extend_rows_with_production_schema(rows: list, start_index: int = 0) -> list:
    """
    Mutate `rows` in place, adding category/sub_category/as_of_date/
    content_scale_proxy_* to each row. `start_index` is this batch's
    0-based offset into the overall 50-row cumulative sequence (0 for
    migrate_schema.py's 10 A0-Phase1 rows, 10 for build_a0_phase2.py's 40
    A0-Phase2 rows), so each generator script tags only its own rows while
    staying consistent with the single CATEGORY_BATCH_PLAN.
    """
    full_sequence = category_sequence_for(start_index + len(rows))
    this_batch_sequence = full_sequence[start_index:start_index + len(rows)]
    for row, (default_category, as_of) in zip(rows, this_batch_sequence):
        domain = row.get("canonical_root_domain")
        # DOMAIN_CATEGORY_OVERRIDES (Item 3, last pre-950 patch) supersedes
        # the batch-level default for individual sites -- currently used
        # only to un-merge the old "Home / DIY & Food" batch into its
        # already-known Home/DIY vs. Food/Recipe split.
        category = DOMAIN_CATEGORY_OVERRIDES.get(domain, default_category)
        if category not in CATEGORY_ENUM:
            raise ValueError(f"category {category!r} not in CATEGORY_ENUM -- update the enum first.")
        row["category"] = category
        row["sub_category"] = "UNKNOWN"
        row["as_of_date"] = as_of
        row["content_scale_proxy_value"] = "UNKNOWN"
        row["content_scale_proxy_method"] = "UNKNOWN"
        row["content_scale_proxy_evidence"] = "UNKNOWN"
        row["content_scale_proxy_source_url"] = "UNKNOWN"
        row["content_scale_proxy_note"] = _NO_PROXY_NOTE
    return rows
