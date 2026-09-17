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
already-documented order -- see CATEGORY_BY_BATCH_POSITION below, which
mirrors migrate_schema.py's row order and build_a0_phase2.py's own
"Category N (...)" print statements).
"""

from datetime import date

# Fixed category taxonomy (Protocol V2 Section 2). This is deliberately a
# CLOSED enum, not free text -- primary_niche remains the free-text detail
# field. New categories are added here only when a new batch's category is
# actually decided (never inferred implicitly at CSV-write time).
CATEGORY_ENUM = [
    "Productivity / PKM",
    "Excel / Spreadsheet",
    "Personal Finance",
    "Home / DIY & Food",
    "Product Review / Buying Guides",
]

# Ordered list of (category, as_of_date, row_count) describing exactly how
# the current 50-row Study A cumulative dataset was assembled, in row
# order (this mirrors migrate_schema.py's FIELDNAMES row order followed by
# build_a0_phase2.py's four categories of 10, each already fixed and
# documented in research_protocol_v2.md Section 7-A/7-B and
# A0_Phase2_report.md -- not a new decision made by this module).
CATEGORY_BATCH_PLAN = [
    ("Productivity / PKM", "2026-09-16", 10),               # A0-Phase1
    ("Excel / Spreadsheet", "2026-09-17", 10),               # A0-Phase2 batch 1
    ("Personal Finance", "2026-09-17", 10),                  # A0-Phase2 batch 2
    ("Home / DIY & Food", "2026-09-17", 10),                 # A0-Phase2 batch 3
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
    for row, (category, as_of) in zip(rows, this_batch_sequence):
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
