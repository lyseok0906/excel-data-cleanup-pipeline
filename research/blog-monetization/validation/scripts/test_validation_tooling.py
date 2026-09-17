#!/usr/bin/env python3
"""
Regression / self-tests for domain_utils.py, migrate_schema.py and
run_gate_v2.py -- covers the 5 blocking issues fixed after GPT's
independent review of commit 40732be (research_protocol_v2.md Section 7-B
records the review). Deliberately kept to plain `unittest` (stdlib only,
no pytest dependency) to match this repo's "no extra dependencies"
constraint.

Run with:
    python -m unittest test_validation_tooling.py -v
or simply:
    python test_validation_tooling.py
"""
import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import domain_utils
import run_gate_v2

HERE = Path(__file__).resolve().parent


class TestDomainCanonicalization(unittest.TestCase):
    """Cases E and F from the task spec."""

    def test_same_domain_variants_collapse(self):
        # Case E
        a = domain_utils.registrable_domain("example.com")
        b = domain_utils.registrable_domain("https://www.example.com/some/path")
        c = domain_utils.registrable_domain("blog.example.com")
        self.assertEqual(a, "example.com")
        self.assertEqual(b, "example.com")
        self.assertEqual(c, "example.com")

    def test_public_suffix_second_level_domains_collapse(self):
        # Case F
        a = domain_utils.registrable_domain("example.co.uk")
        b = domain_utils.registrable_domain("https://www.example.co.uk/")
        self.assertEqual(a, "example.co.uk")
        self.assertEqual(b, "example.co.uk")

    def test_different_tlds_are_distinct(self):
        a = domain_utils.registrable_domain("example.com")
        b = domain_utils.registrable_domain("example.net")
        self.assertNotEqual(a, b)

    def test_co_uk_not_confused_with_dot_com(self):
        # A .co.uk site must never collapse onto a .com site with the same label.
        self.assertNotEqual(
            domain_utils.registrable_domain("example.co.uk"),
            domain_utils.registrable_domain("example.com"),
        )


class TestProvenanceGate(unittest.TestCase):
    """Cases A and B from the task spec."""

    def _row(self, **overrides):
        base = {f: "N" for f in run_gate_v2.BOOL_FIELDS}
        for f in run_gate_v2.BOOL_FIELDS:
            base[f + "_evidence"] = "UNKNOWN"
            base[f + "_source_url"] = ""
            base[f + "_note"] = ""
        base.update({
            "canonical_root_domain": "example.com",
            "traffic_scope": "CONTENT_ONLY",
            "traffic_tier": "MID",
            "contrast_pattern": "NOT_APPLICABLE",
            "traffic_value_raw": "60000",
            "traffic_evidence": "UNKNOWN",
            "traffic_source_url": "",
            "traffic_research_date": "2026-09-16",
            "revenue_value": "UNKNOWN",
            "revenue_evidence": "UNKNOWN",
            "revenue_source_url": "",
            "revenue_research_date": "2026-09-16",
            "start_year_value": "2020",
            "start_year_evidence": "UNKNOWN",
            "start_year_source_url": "",
        })
        base.update(overrides)
        return base

    def test_A_evidence_without_dedicated_url_fails_even_with_url_in_note(self):
        row = self._row(
            affiliate="Y",
            affiliate_evidence="A",
            affiliate_source_url="",
            affiliate_note="source: https://example.com/about (operator statement)",
        )
        violations = run_gate_v2.check_provenance([row])
        self.assertTrue(
            any(v[0] == "example.com" and v[1] == "affiliate" for v in violations),
            "note-only URL must NOT satisfy provenance for A/B evidence",
        )

    def test_B_evidence_with_dedicated_url_passes(self):
        row = self._row(
            affiliate="Y",
            affiliate_evidence="A",
            affiliate_source_url="https://example.com/about",
            affiliate_note="operator statement",
        )
        violations = run_gate_v2.check_provenance([row])
        self.assertFalse(
            any(v[0] == "example.com" and v[1] == "affiliate" for v in violations),
            "a valid dedicated source_url must satisfy provenance",
        )


class TestTrafficScopeTier(unittest.TestCase):
    """Cases C and D from the task spec."""

    def test_C_whole_domain_forces_unknown_tier(self):
        import migrate_schema
        self.assertEqual(migrate_schema.traffic_tier_for("WHOLE_DOMAIN_INCLUDES_PRODUCT", 5_000_000), "UNKNOWN")

    def test_D_unknown_scope_forces_unknown_tier(self):
        import migrate_schema
        self.assertEqual(migrate_schema.traffic_tier_for("UNKNOWN", 5_000_000), "UNKNOWN")

    def test_content_only_computes_normally(self):
        import migrate_schema
        self.assertEqual(migrate_schema.traffic_tier_for("CONTENT_ONLY", 5_000), "LOW")
        self.assertEqual(migrate_schema.traffic_tier_for("CONTENT_ONLY", 50_000), "MID")
        self.assertEqual(migrate_schema.traffic_tier_for("CONTENT_ONLY", 500_000), "HIGH")


class TestGateExitCode(unittest.TestCase):
    """Cases G and H from the task spec -- exercised as real subprocess calls
    so the test actually proves the *process* exit code, not just the
    in-memory return value."""

    def test_H_success_exit_code_zero(self):
        real_csv = HERE.parent / "validation_10_v2.csv"
        result = subprocess.run(
            [sys.executable, str(HERE / "run_gate_v2.py"), str(real_csv), "--report", str(HERE / "_tmp_report_pass.txt")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        (HERE / "_tmp_report_pass.txt").unlink(missing_ok=True)

    def test_G_intentional_bad_fixture_exit_code_nonzero(self):
        bad_csv = HERE / "_tmp_bad_fixture.csv"
        with real_csv_reader(HERE.parent / "validation_10_v2.csv") as (fieldnames, rows):
            # Corrupt one row: mixed value+evidence AND a duplicate domain AND
            # a note-only-URL provenance violation, to be sure the gate
            # actually inspects content rather than just running clean.
            rows[0]["affiliate"] = "Y (D)"
            rows[1]["canonical_root_domain"] = rows[0]["canonical_root_domain"]  # force a duplicate
            with bad_csv.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames)
                w.writeheader()
                w.writerows(rows)
        try:
            result = subprocess.run(
                [sys.executable, str(HERE / "run_gate_v2.py"), str(bad_csv), "--report", str(HERE / "_tmp_report_fail.txt")],
                capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        finally:
            bad_csv.unlink(missing_ok=True)
            (HERE / "_tmp_report_fail.txt").unlink(missing_ok=True)


class real_csv_reader:
    """Small context manager: reads a CSV into (fieldnames, list[dict]) for mutation in tests."""

    def __init__(self, path: Path):
        self.path = path

    def __enter__(self):
        with self.path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            self.fieldnames = reader.fieldnames
            self.rows = list(reader)
        return self.fieldnames, self.rows

    def __exit__(self, *exc):
        return False


class TestMigrationReproducibility(unittest.TestCase):
    """Case I from the task spec: re-running migrate_schema.py against the
    committed validation_10.csv must reproduce the committed
    validation_10_v2.csv exactly."""

    def test_I_migration_matches_committed_output(self):
        import migrate_schema

        with tempfile.TemporaryDirectory() as td:
            dst = Path(td) / "regen.csv"
            old = migrate_schema.load_source(HERE.parent / "validation_10.csv")
            rows = migrate_schema.build_rows(old)
            with dst.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=migrate_schema.FIELDNAMES)
                w.writeheader()
                for r in rows:
                    w.writerow({k: r[k] for k in migrate_schema.FIELDNAMES})

            with dst.open(newline="", encoding="utf-8") as f:
                regen = {r["canonical_root_domain"]: r for r in csv.DictReader(f)}
            with (HERE.parent / "validation_10_v2.csv").open(newline="", encoding="utf-8") as f:
                committed = {r["canonical_root_domain"]: r for r in csv.DictReader(f)}

            self.assertEqual(set(regen.keys()), set(committed.keys()))
            diffs = []
            for d in committed:
                for k in committed[d]:
                    if committed[d][k] != regen[d].get(k):
                        diffs.append((d, k, committed[d][k], regen[d].get(k)))
            self.assertEqual(diffs, [], msg=f"{len(diffs)} field(s) differ from committed output: {diffs}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
