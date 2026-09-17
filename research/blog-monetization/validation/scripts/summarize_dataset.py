#!/usr/bin/env python3
"""
Automated, dataset-neutral summary/report generator for any Protocol V2
canonical-schema CSV (validation_10_v2.csv, validation_50_v2.csv, and any
future N-site dataset).

Built during the pre-950 hardening round (2026-09-17) specifically to
replace ALL manual/hand-typed aggregation in reports. The previous
hand-written A0_Phase2_report.md contained two concrete errors that this
script is designed to make structurally impossible:

  1. An arithmetic error in the evidence-tier distribution total
     ("11 fields x 50 = 550 cells" claimed vs. 500 actually shown). This
     script derives both the field list AND the row count directly from
     evidence_harden.ALL_GROUPS and the CSV itself, and prints the
     multiplication it used, so the total is always self-consistent and
     auditable.
  2. Conflation of `sampling_stratum == "Contrast Cohort"` counts with
     `is_contrast_case == "Y"` counts. This script reports both counts
     separately, side by side, with an explicit note that they are
     different axes (one is a sampling-design label, the other is a
     researched boolean finding) and are not expected to be equal.

Usage:
    python summarize_dataset.py [path/to/validation_NN_v2.csv] [--out FILE]

No third-party dependencies. No network access. No fabricated data --
every number here is computed directly from the CSV rows.
"""

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

import evidence_harden

DEFAULT_CSV = Path(__file__).parent.parent / "validation_10_v2.csv"

UNKNOWN = "UNKNOWN"

# Value-bearing fields we report UNKNOWN-rate / completion-rate for,
# beyond the evidence-harden groups (which cover the 10 evidence-bearing
# value fields already).
EXTRA_VALUE_FIELDS = [
    "traffic_tier",
    "traffic_scope",
]


def load_rows(path: Path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows


def pct(n, d):
    if d == 0:
        return "n/a"
    return f"{100.0 * n / d:.1f}%"


def section_row_count(rows, lines):
    lines.append(f"Row count: {len(rows)}")
    lines.append("")


def section_category_distribution(rows, lines):
    lines.append("## Category distribution (primary_niche)")
    c = Counter(r.get("primary_niche", UNKNOWN) for r in rows)
    for k, v in sorted(c.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"  {k}: {v} ({pct(v, len(rows))})")
    lines.append(f"  TOTAL: {sum(c.values())} (must equal row count {len(rows)})")
    lines.append("")


def section_sampling_stratum(rows, lines):
    lines.append("## sampling_stratum distribution")
    c = Counter(r.get("sampling_stratum", UNKNOWN) for r in rows)
    for k, v in sorted(c.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"  {k}: {v} ({pct(v, len(rows))})")
    lines.append(f"  TOTAL: {sum(c.values())} (must equal row count {len(rows)})")
    lines.append("")


def section_contrast_case_vs_stratum(rows, lines):
    lines.append("## is_contrast_case vs. sampling_stratum=Contrast Cohort (kept separate -- NOT the same axis)")
    ic = Counter(r.get("is_contrast_case", UNKNOWN) for r in rows)
    stratum_contrast = sum(1 for r in rows if r.get("sampling_stratum") == "Contrast Cohort")
    lines.append("  is_contrast_case (researched boolean finding):")
    for k, v in sorted(ic.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"    {k}: {v} ({pct(v, len(rows))})")
    lines.append(f"  sampling_stratum == 'Contrast Cohort' (sampling-design label): {stratum_contrast} ({pct(stratum_contrast, len(rows))})")
    overlap = sum(1 for r in rows if r.get("sampling_stratum") == "Contrast Cohort" and r.get("is_contrast_case") == "Y")
    lines.append(f"  Overlap (sampling_stratum=Contrast Cohort AND is_contrast_case=Y): {overlap}")
    lines.append("  NOTE: these two counts are independent axes and are not expected to match.")
    lines.append("")


def section_traffic_scope_tier(rows, lines):
    lines.append("## traffic_scope distribution")
    c = Counter(r.get("traffic_scope", UNKNOWN) for r in rows)
    for k, v in sorted(c.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"  {k}: {v} ({pct(v, len(rows))})")
    lines.append("")

    lines.append("## traffic_tier distribution")
    c2 = Counter(r.get("traffic_tier", UNKNOWN) for r in rows)
    for k, v in sorted(c2.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"  {k}: {v} ({pct(v, len(rows))})")
    lines.append("")


def section_unknown_rate(rows, lines):
    lines.append("## UNKNOWN rate per value field")
    value_fields = [g[0] for g in evidence_harden.ALL_GROUPS] + EXTRA_VALUE_FIELDS
    for field in value_fields:
        n_unknown = sum(1 for r in rows if str(r.get(field, UNKNOWN)).strip() == UNKNOWN)
        lines.append(f"  {field}: {n_unknown}/{len(rows)} UNKNOWN ({pct(n_unknown, len(rows))})")
    lines.append("")


def section_field_completion(rows, lines):
    lines.append("## Field completion rate (non-UNKNOWN / total) per value field")
    value_fields = [g[0] for g in evidence_harden.ALL_GROUPS] + EXTRA_VALUE_FIELDS
    for field in value_fields:
        n_known = sum(1 for r in rows if str(r.get(field, UNKNOWN)).strip() != UNKNOWN)
        lines.append(f"  {field}: {n_known}/{len(rows)} completed ({pct(n_known, len(rows))})")
    lines.append("")


def section_evidence_distribution(rows, lines):
    groups = evidence_harden.ALL_GROUPS
    n_fields = len(groups)
    n_rows = len(rows)
    expected_total = n_fields * n_rows
    lines.append("## Evidence-tier distribution (across all evidence-bearing fields)")
    lines.append(
        f"  Evidence-bearing fields counted: {n_fields} "
        f"({', '.join(g[1] for g in groups)})"
    )
    lines.append(f"  Rows: {n_rows}")
    lines.append(f"  Expected total evidence-tier cells = {n_fields} fields x {n_rows} rows = {expected_total}")

    overall = Counter()
    per_field = {}
    for value_field, ev_field, _url_field, _note_field in groups:
        c = Counter(str(r.get(ev_field, UNKNOWN)).strip() for r in rows)
        per_field[ev_field] = c
        overall.update(c)

    actual_total = sum(overall.values())
    lines.append(f"  Actual total evidence-tier cells counted: {actual_total}"
                 + ("  [MATCH]" if actual_total == expected_total else "  [MISMATCH -- investigate]"))
    lines.append("")
    lines.append("  Overall tier distribution (all fields combined):")
    for k, v in sorted(overall.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"    {k}: {v} ({pct(v, actual_total)})")
    lines.append("")
    lines.append("  Per-field tier distribution:")
    for ev_field, c in per_field.items():
        total_f = sum(c.values())
        parts = ", ".join(f"{k}={v}" for k, v in sorted(c.items(), key=lambda kv: (-kv[1], kv[0])))
        lines.append(f"    {ev_field} (n={total_f}): {parts}")
    lines.append("")


def section_denominators(rows, lines):
    lines.append("## Denominator notes")
    lines.append(
        "  All rates above use the FULL row count as the denominator unless stated "
        "otherwise. Rates that are conceptually conditional on another field (e.g. "
        "'of sites with a known traffic_scope, how many have a known traffic_tier') "
        "are called out explicitly below rather than silently using a filtered "
        "denominator elsewhere."
    )
    known_scope = sum(1 for r in rows if str(r.get("traffic_scope", UNKNOWN)).strip() != UNKNOWN)
    known_scope_and_tier = sum(
        1 for r in rows
        if str(r.get("traffic_scope", UNKNOWN)).strip() != UNKNOWN
        and str(r.get("traffic_tier", UNKNOWN)).strip() != UNKNOWN
    )
    lines.append(
        f"  Of {len(rows)} rows, {known_scope} have a known (non-UNKNOWN) traffic_scope; "
        f"of those, {known_scope_and_tier} also have a known traffic_tier "
        f"({pct(known_scope_and_tier, known_scope)} of the known-scope subset)."
    )
    lines.append("")


def build_summary(rows) -> str:
    lines = []
    lines.append("=" * 70)
    lines.append("AUTOMATED DATASET SUMMARY (generated by summarize_dataset.py)")
    lines.append("All figures below are computed directly from the CSV. No manual")
    lines.append("arithmetic is performed anywhere in this report.")
    lines.append("=" * 70)
    lines.append("")
    section_row_count(rows, lines)
    section_category_distribution(rows, lines)
    section_sampling_stratum(rows, lines)
    section_contrast_case_vs_stratum(rows, lines)
    section_traffic_scope_tier(rows, lines)
    section_unknown_rate(rows, lines)
    section_field_completion(rows, lines)
    section_evidence_distribution(rows, lines)
    section_denominators(rows, lines)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Automated Protocol V2 dataset summary.")
    parser.add_argument("csv_path", nargs="?", default=str(DEFAULT_CSV))
    parser.add_argument("--out", default=None, help="Optional path to write the report to (also printed to stdout).")
    args = parser.parse_args()

    path = Path(args.csv_path)
    rows = load_rows(path)
    report = build_summary(rows)
    print(report)

    if args.out:
        Path(args.out).write_text(report + "\n", encoding="utf-8")
        print(f"\nWrote summary to {args.out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
