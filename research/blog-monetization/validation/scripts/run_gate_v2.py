#!/usr/bin/env python3
"""
Protocol V2 Validation Gate runner (research_protocol_v2.md, Section 7).

Reads a Protocol-V2-schema CSV (default: ../validation_10_v2.csv, relative
to this script) and runs the full gate checklist against it, printing a
human-readable report and writing it to ../gate_report_v2.txt.

Exit code is machine-detectable, as required for automation:
    0   -> every gate check passed
    1   -> at least one gate check failed

Usage:
    python run_gate_v2.py [CSV_PATH] [--report PATH]
"""
import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

import domain_utils

HERE = Path(__file__).resolve().parent
DEFAULT_CSV = HERE.parent / "validation_10_v2.csv"
DEFAULT_REPORT = HERE.parent / "gate_report_v2.txt"

VALID_BOOL = {"Y", "N", "UNKNOWN"}
VALID_EV = {"A", "B", "C", "D", "UNKNOWN"}
VALID_TRAFFIC_SCOPE = {"CONTENT_ONLY", "WHOLE_DOMAIN_INCLUDES_PRODUCT", "SUBDIRECTORY_ESTIMATE", "UNKNOWN"}
VALID_CONTRAST_PATTERN = {"shutdown", "traffic_decline", "cadence_drop", "low_traction_despite_age", "historically_declined", "NOT_APPLICABLE"}
BOOL_FIELDS = ["is_niche_authority", "is_contrast_case", "display_ads", "affiliate", "own_product", "course_or_community", "newsletter_email_capture"]
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
URL_RE = re.compile(r"^https?://", re.IGNORECASE)


def load_rows(csv_path: Path):
    with csv_path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def check_enum(rows):
    """Section 7 item 1: boolean/evidence/enum fields use only defined values."""
    violations = []
    for r in rows:
        for f in BOOL_FIELDS:
            v = r[f].strip()
            if v not in VALID_BOOL:
                violations.append((r["canonical_root_domain"], f, v))
            ev = r[f + "_evidence"].strip()
            if ev not in VALID_EV:
                violations.append((r["canonical_root_domain"], f + "_evidence", ev))
        if r["traffic_scope"].strip() not in VALID_TRAFFIC_SCOPE:
            violations.append((r["canonical_root_domain"], "traffic_scope", r["traffic_scope"]))
        if r["contrast_pattern"].strip() not in VALID_CONTRAST_PATTERN:
            violations.append((r["canonical_root_domain"], "contrast_pattern", r["contrast_pattern"]))
        for f in ["traffic_evidence", "revenue_evidence", "start_year_evidence"]:
            ev = r[f].strip()
            if ev not in VALID_EV:
                violations.append((r["canonical_root_domain"], f, ev))
    return violations


def check_mixed_format(rows):
    """Section 7 item 2: no 'Y (D)'-style mixed value+evidence strings."""
    mixed = []
    pat = re.compile(r"\([A-D]\)")
    for r in rows:
        for f in BOOL_FIELDS + ["start_year_value", "traffic_value_raw", "revenue_value"]:
            v = r.get(f, "")
            if pat.search(v):
                mixed.append((r["canonical_root_domain"], f, v))
    return mixed


def check_duplicates(rows):
    """
    Section 7 item 3 + Section 6: duplicate detection on the REGISTRABLE
    domain (eTLD+1), not a naive string compare, per domain_utils. Also
    flags any canonical_root_domain value that isn't already in clean
    root form (this is a data-quality check on the field itself, separate
    from the cross-row duplicate check).
    """
    domains_raw = [r["canonical_root_domain"].strip() for r in rows]
    format_violations = [d for d in domains_raw if not domain_utils.is_clean_root_form(d)]

    registrable = [domain_utils.registrable_domain(d) for d in domains_raw]
    dupe_counts = Counter(registrable)
    dupes = {d: c for d, c in dupe_counts.items() if c > 1}
    return format_violations, dupes


def check_provenance(rows):
    """
    Section 7 item 4, hardened: for every evidence-bearing field, if
    evidence is A or B, the field's DEDICATED `_source_url` column must
    itself be a valid http(s) URL. A URL merely mentioned inside the
    free-text `_note` field does NOT satisfy this check -- Protocol V2
    Section 3 explicitly prohibits hiding provenance in note text.
    """
    missing = []
    field_url_pairs = [(f, f + "_source_url", f + "_evidence") for f in BOOL_FIELDS] + [
        ("traffic", "traffic_source_url", "traffic_evidence"),
        ("revenue", "revenue_source_url", "revenue_evidence"),
        ("start_year", "start_year_source_url", "start_year_evidence"),
    ]
    for r in rows:
        for base, urlfield, evfield in field_url_pairs:
            ev = r[evfield].strip()
            if ev in ("A", "B"):
                url = r.get(urlfield, "").strip()
                if not URL_RE.match(url):
                    missing.append((r["canonical_root_domain"], base, ev, url))
    return missing


def check_dates(rows):
    """Section 7 item 5: research_date fields are ISO or explicit UNKNOWN."""
    bad = []
    for r in rows:
        for f in ["traffic_research_date", "revenue_research_date"]:
            v = r[f].strip()
            if v != "UNKNOWN" and not ISO_DATE_RE.match(v):
                bad.append((r["canonical_root_domain"], f, v))
    return bad


def check_rule8(rows):
    """Section 7 item 6 / Section 3-2: UNKNOWN value must carry UNKNOWN evidence."""
    violations = []
    pairs = [(f, f + "_evidence") for f in BOOL_FIELDS] + [
        ("traffic_value_raw", "traffic_evidence"),
        ("revenue_value", "revenue_evidence"),
        ("start_year_value", "start_year_evidence"),
    ]
    for r in rows:
        for vf, ef in pairs:
            v = r[vf].strip()
            ev = r[ef].strip()
            if v == "UNKNOWN" and ev != "UNKNOWN":
                violations.append((r["canonical_root_domain"], vf, v, ef, ev))
    return violations


def check_traffic_scope_tier(rows):
    """Section 7 item 7 / Section 4-1: scope-aware traffic_tier consistency."""
    violations = []
    for r in rows:
        scope = r["traffic_scope"].strip()
        tier = r["traffic_tier"].strip()
        if scope in ("WHOLE_DOMAIN_INCLUDES_PRODUCT", "UNKNOWN") and tier != "UNKNOWN":
            violations.append((r["canonical_root_domain"], scope, tier, "expected UNKNOWN per Section 4-1"))
        if scope == "WHOLE_DOMAIN_INCLUDES_PRODUCT" and r["traffic_value_raw"].strip() in ("", "UNKNOWN"):
            violations.append((r["canonical_root_domain"], scope, r["traffic_value_raw"], "raw value should be preserved, not blanked, for WHOLE_DOMAIN_INCLUDES_PRODUCT"))
    return violations


def check_dimension_independence(rows):
    """Section 7 item 8: sampling_stratum / traffic_tier / is_niche_authority / is_contrast_case are independent fields (informational, not a pass/fail check)."""
    return [
        (r["canonical_root_domain"], r["sampling_stratum"], r["traffic_tier"], r["is_niche_authority"], r["is_contrast_case"])
        for r in rows
    ]


def check_denominator_automation(rows, fields=("affiliate", "display_ads", "own_product", "is_niche_authority", "is_contrast_case")):
    """Section 7 item 9: denominators computable via direct column filter, no string parsing."""
    results = {}
    for f in fields:
        vals = [r[f].strip() for r in rows]
        denom = sum(1 for v in vals if v in ("Y", "N"))
        num = sum(1 for v in vals if v == "Y")
        results[f] = (num, denom)
    return results


def run_gate(rows):
    """Runs every check and returns (report_lines, all_passed)."""
    lines = []
    all_passed = True

    def section(title):
        lines.append(f"--- {title} ---")

    lines.append(f"=== Row count: {len(rows)} ===\n")

    section("1. Enum validation")
    v = check_enum(rows)
    if v:
        all_passed = False
        lines.append(f"FAIL: {len(v)} violations:")
        lines.extend(f"  {x}" for x in v)
    else:
        lines.append("PASS: all boolean/evidence/enum fields (incl. traffic_scope, contrast_pattern) use only allowed values.")
    lines.append("")

    section("2. Mixed value+evidence in single cell check")
    v = check_mixed_format(rows)
    if v:
        all_passed = False
        lines.append(f"FAIL: {v}")
    else:
        lines.append("PASS: no mixed value+evidence strings found.")
    lines.append("")

    section("3. Duplicate canonical_root_domain check (registrable-domain based)")
    format_violations, dupes = check_duplicates(rows)
    if format_violations:
        all_passed = False
        lines.append(f"FAIL: {len(format_violations)} canonical_root_domain values are not clean root form: {format_violations}")
    else:
        lines.append("PASS: all canonical_root_domain values are clean root form (no www./scheme/path).")
    if dupes:
        all_passed = False
        lines.append(f"FAIL: {len(dupes)} registrable-domain collisions: {dupes}")
    else:
        lines.append(f"PASS: all {len(rows)} rows resolve to distinct registrable (eTLD+1) domains (domain_utils.registrable_domain).")
    lines.append("")

    section("4. Provenance / source_url validation (dedicated column required for A/B evidence -- note fallback NOT accepted)")
    v = check_provenance(rows)
    if v:
        all_passed = False
        lines.append(f"FAIL: {len(v)} A/B-evidence fields missing a valid dedicated source_url:")
        lines.extend(f"  {x}" for x in v)
    else:
        lines.append("PASS: every field carrying A or B evidence has a valid http(s) URL in its own dedicated _source_url column (note-text URLs do not count).")
    lines.append("")

    section("5. Date-format validation")
    v = check_dates(rows)
    if v:
        all_passed = False
        lines.append(f"FAIL: {len(v)} non-ISO or malformed date cells:")
        lines.extend(f"  {x}" for x in v)
    else:
        lines.append("PASS: all traffic_research_date / revenue_research_date cells are clean ISO (YYYY-MM-DD) or explicit UNKNOWN.")
    lines.append("")

    section("6. UNKNOWN value implies UNKNOWN evidence (Rule #8)")
    v = check_rule8(rows)
    if v:
        all_passed = False
        lines.append(f"FAIL: {len(v)} Rule #8 violations:")
        lines.extend(f"  {x}" for x in v)
    else:
        lines.append("PASS: every UNKNOWN-valued field carries UNKNOWN evidence.")
    lines.append("")

    section("7. traffic_scope / traffic_tier consistency check (Section 4-1 rule)")
    scopes = Counter(r["traffic_scope"] for r in rows)
    lines.append(f"traffic_scope distribution: {dict(scopes)}")
    v = check_traffic_scope_tier(rows)
    if v:
        all_passed = False
        lines.append(f"FAIL: {len(v)} traffic_scope/traffic_tier rule violations:")
        lines.extend(f"  {x}" for x in v)
    else:
        lines.append("PASS: traffic_tier correctly forced to UNKNOWN wherever traffic_scope is WHOLE_DOMAIN_INCLUDES_PRODUCT or UNKNOWN, and raw traffic values remain preserved.")
    whole_domain = [r["canonical_root_domain"] for r in rows if r["traffic_scope"] == "WHOLE_DOMAIN_INCLUDES_PRODUCT"]
    lines.append(f"Sites flagged as whole-domain (excluded from content-level traffic_tier comparisons, raw value retained): {whole_domain}")
    lines.append("")

    section("8. contrast_pattern structure check")
    for r in rows:
        if r["is_contrast_case"] == "Y":
            lines.append(f"  {r['canonical_root_domain']}: contrast_pattern={r['contrast_pattern']}, evidence_period='{r['contrast_evidence_period'][:80]}...'")
    lines.append("")

    section("9. Dimension-independence check (sampling_stratum vs traffic_tier vs is_niche_authority vs is_contrast_case)")
    for d, stratum, tier, auth, contrast in check_dimension_independence(rows):
        lines.append(f"  {d}: stratum={stratum} | traffic_tier={tier} | is_niche_authority={auth} | is_contrast_case={contrast}")
    mismatch = [r["canonical_root_domain"] for r in rows if r["sampling_stratum"] == "Large/Traffic Leader" and r["traffic_tier"] == "LOW"]
    lines.append(f"Example of dimension mismatch surfaced (stratum=Large/Traffic Leader but traffic_tier=LOW): {mismatch}")
    lines.append("")

    section("10. Denominator automation test")
    for f, (num, denom) in check_denominator_automation(rows).items():
        lines.append(f"  {f}: {num} of {denom} confirmed = Y (direct column filter, no parsing)")
    lines.append("PASS: denominators computable via direct column filter across all migrated fields.")
    lines.append("")

    lines.append("A0-Phase1 FINAL PASS" if all_passed else "A0-Phase1 GATE FAILED -- see violations above")
    return lines, all_passed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", nargs="?", type=Path, default=DEFAULT_CSV, help="Path to the Protocol-V2-schema CSV (default: ../validation_10_v2.csv relative to this script)")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT, help="Where to write the text report (default: ../gate_report_v2.txt relative to this script)")
    args = parser.parse_args()

    rows = load_rows(args.csv_path)
    lines, all_passed = run_gate(rows)

    report_text = "\n".join(lines)
    print(report_text)
    args.report.write_text(report_text, encoding="utf-8")
    print(f"\nWrote {args.report}")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
