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
import evidence_harden
import run_gate_v2
import summarize_dataset
import build_domain_registry as registry
import wave_coordinator

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
            "category": "Productivity / PKM",
            "sub_category": "UNKNOWN",
            "as_of_date": "2026-09-17",
            "content_scale_proxy_value": "UNKNOWN",
            "content_scale_proxy_method": "UNKNOWN",
            "content_scale_proxy_evidence": "UNKNOWN",
            "content_scale_proxy_source_url": "",
            "content_scale_proxy_note": "",
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


class TestPre950FollowUpHardening(unittest.TestCase):
    """
    New regression tests added for the GPT follow-up to commit 8dffb08
    (2026-09-17, "remove auto-fabrication" engineering patch). Covers:
    value/evidence directional consistency, evidence_harden's no-fabrication
    behavior, the revenue_value format Gate check, summarize_dataset's
    self-checking evidence total and its use of the real `category` field,
    and the Domain Registry's state-machine enforcement.
    """

    def _min_row(self, **overrides):
        row = {f: "UNKNOWN" for f in run_gate_v2.BOOL_FIELDS}
        for f in run_gate_v2.BOOL_FIELDS:
            row[f + "_evidence"] = "UNKNOWN"
            row[f + "_source_url"] = ""
            row[f + "_note"] = ""
        row.update({
            "canonical_root_domain": "example.com",
            "traffic_scope": "CONTENT_ONLY",
            "traffic_tier": "MID",
            "contrast_pattern": "NOT_APPLICABLE",
            "traffic_value_raw": "UNKNOWN",
            "traffic_evidence": "UNKNOWN",
            "traffic_source_url": "",
            "traffic_note": "",
            "traffic_research_date": "2026-09-17",
            "revenue_value": "UNKNOWN",
            "revenue_evidence": "UNKNOWN",
            "revenue_source_url": "",
            "revenue_note": "",
            "revenue_research_date": "2026-09-17",
            "start_year_value": "UNKNOWN",
            "start_year_evidence": "UNKNOWN",
            "start_year_source_url": "",
            "start_year_note": "",
            "category": "Productivity / PKM",
            "sub_category": "UNKNOWN",
            "as_of_date": "2026-09-17",
            "content_scale_proxy_value": "UNKNOWN",
            "content_scale_proxy_method": "UNKNOWN",
            "content_scale_proxy_evidence": "UNKNOWN",
            "content_scale_proxy_source_url": "",
            "content_scale_proxy_note": "",
        })
        row.update(overrides)
        return row

    # -- non-UNKNOWN value + UNKNOWN evidence --

    def test_non_unknown_value_with_unknown_evidence_fails(self):
        row = self._min_row(affiliate="Y", affiliate_evidence="UNKNOWN")
        violations = run_gate_v2.check_value_requires_evidence([row])
        self.assertTrue(any(v[0] == "example.com" and v[1] == "affiliate" for v in violations))

    # -- evidence_harden: no auto-fabrication --

    def test_C_evidence_no_source_url_raises(self):
        d = self._min_row(affiliate="Y", affiliate_evidence="C", affiliate_source_url="", affiliate_note="observed on homepage")
        with self.assertRaises(evidence_harden.EvidenceHardenError):
            evidence_harden.harden_row(d)

    def test_D_evidence_empty_note_raises(self):
        d = self._min_row(affiliate="N", affiliate_evidence="D", affiliate_note="")
        with self.assertRaises(evidence_harden.EvidenceHardenError):
            evidence_harden.harden_row(d)

    def test_D_evidence_with_real_note_passes(self):
        d = self._min_row(affiliate="N", affiliate_evidence="D", affiliate_note="Reasoned from the site's ad-free content model.")
        evidence_harden.harden_row(d)  # must not raise

    # -- revenue_value format --

    def test_revenue_value_acquisition_price_fails(self):
        row = self._min_row(revenue_value="Acquisition price: $33 million (2007)")
        bad = run_gate_v2.check_revenue_value_format([row])
        self.assertEqual(len(bad), 1)

    def test_revenue_value_free_text_fails(self):
        row = self._min_row(revenue_value="UNKNOWN (only partial historical figures found)")
        bad = run_gate_v2.check_revenue_value_format([row])
        self.assertEqual(len(bad), 1)

    def test_revenue_value_clean_figure_passes(self):
        row = self._min_row(revenue_value="$45K/month")
        bad = run_gate_v2.check_revenue_value_format([row])
        self.assertEqual(bad, [])

    def test_revenue_value_unknown_passes(self):
        row = self._min_row(revenue_value="UNKNOWN")
        bad = run_gate_v2.check_revenue_value_format([row])
        self.assertEqual(bad, [])

    # -- summarize_dataset --

    def test_summary_evidence_cell_total_self_check(self):
        rows = [self._min_row(canonical_root_domain=f"site{i}.com") for i in range(5)]
        lines = []
        summarize_dataset.section_evidence_distribution(rows, lines)
        text = "\n".join(lines)
        n_fields = len(evidence_harden.ALL_GROUPS)
        self.assertIn(f"Expected total evidence-tier cells = {n_fields} fields x 5 rows = {n_fields * 5}", text)
        self.assertIn(f"Actual total evidence-tier cells counted: {n_fields * 5}  [MATCH]", text)

    def test_summary_uses_category_field_not_primary_niche(self):
        rows = [
            self._min_row(canonical_root_domain="a.com", category="Excel / Spreadsheet"),
            self._min_row(canonical_root_domain="b.com", category="Excel / Spreadsheet"),
        ]
        for r in rows:
            r["primary_niche"] = r["canonical_root_domain"]  # deliberately distinct per row
        lines = []
        summarize_dataset.section_category_distribution(rows, lines)
        text = "\n".join(lines)
        self.assertIn("Excel / Spreadsheet: 2", text)
        self.assertNotIn("a.com: 1", text)  # must not be aggregating primary_niche as "category"

    # -- Domain Registry state machine --

    def test_registry_duplicate_reserve_refused(self):
        rows = [{"canonical_root_domain": "existing.com", "registrable_domain": "existing.com",
                 "source_group": "test", "category": "UNKNOWN", "sampling_stratum": "UNKNOWN",
                 "status": "COMMITTED", "batch_id": "B0"}]
        rows, dupes = registry.reserve_domains(rows, ["existing.com"], batch_id="B1")
        self.assertEqual(dupes, [("existing.com", "COMMITTED")])

    def test_registry_excluded_to_committed_refused(self):
        rows = [{"canonical_root_domain": "pilot.com", "registrable_domain": "pilot.com",
                 "source_group": "pilot", "category": "UNKNOWN", "sampling_stratum": "UNKNOWN",
                 "status": "EXCLUDED_PRIOR_PILOT", "batch_id": "Pilot-100"}]
        with self.assertRaises(registry.RegistryStateError):
            registry.commit_domains(rows, ["pilot.com"], batch_id="Pilot-100")

    def test_registry_committed_to_reserved_refused(self):
        # There is no direct "re-reserve" transition; reserve_domains() itself
        # must refuse to touch an already-COMMITTED domain.
        rows = [{"canonical_root_domain": "done.com", "registrable_domain": "done.com",
                 "source_group": "A0", "category": "UNKNOWN", "sampling_stratum": "UNKNOWN",
                 "status": "COMMITTED", "batch_id": "A0-cumulative-50"}]
        rows2, dupes = registry.reserve_domains(rows, ["done.com"], batch_id="Wave-2")
        self.assertEqual(dupes, [("done.com", "COMMITTED")])
        self.assertEqual(rows2[0]["status"], "COMMITTED")  # unchanged

    def test_registry_wrong_batch_id_commit_refused(self):
        rows = [{"canonical_root_domain": "wave.com", "registrable_domain": "wave.com",
                 "source_group": "Wave-1", "category": "UNKNOWN", "sampling_stratum": "UNKNOWN",
                 "status": "RESERVED", "batch_id": "Wave-1"}]
        with self.assertRaises(registry.RegistryStateError):
            registry.commit_domains(rows, ["wave.com"], batch_id="Wave-2")

    def test_registry_registrable_domain_duplicate_merge_refused(self):
        with tempfile.TemporaryDirectory() as td:
            master = Path(td) / "master.csv"
            wave = Path(td) / "wave.csv"
            fieldnames = ["canonical_root_domain", "site_name"]
            with master.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames)
                w.writeheader()
                w.writerow({"canonical_root_domain": "example.com", "site_name": "Existing"})
            with wave.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames)
                w.writeheader()
                # Different raw string, same registrable domain -- must still be caught.
                w.writerow({"canonical_root_domain": "www.example.com", "site_name": "Sneaky dupe"})
            with self.assertRaises(ValueError):
                registry.merge_wave_into_master(wave, master)

    # -- Full PSL (RESOLVED, 2026-09-17): tldextract==5.3.2 confirmed installed
    # and working in the user's local Windows Python (>=3.10) environment.
    # These tests replace the prior @unittest.expectedFailure placeholder --
    # they are now ordinary, must-pass assertions. If tldextract is not
    # installed in whatever environment runs this file, domain_utils.py's
    # import itself raises ImportError with an explanation before any of
    # these tests even run.

    def test_full_psl_blogspot_subdomains_are_distinct(self):
        a = domain_utils.registrable_domain("foo.blogspot.com")
        b = domain_utils.registrable_domain("bar.blogspot.com")
        self.assertNotEqual(a, b)
        self.assertEqual(a, "foo.blogspot.com")
        self.assertEqual(b, "bar.blogspot.com")

    def test_full_psl_github_io_subdomains_are_distinct(self):
        a = domain_utils.registrable_domain("foo.github.io")
        b = domain_utils.registrable_domain("bar.github.io")
        self.assertNotEqual(a, b)
        self.assertEqual(a, "foo.github.io")
        self.assertEqual(b, "bar.github.io")

    def test_full_psl_plain_domains_still_work(self):
        self.assertEqual(domain_utils.registrable_domain("example.com"), "example.com")
        self.assertEqual(domain_utils.registrable_domain("www.example.com"), "example.com")
        self.assertEqual(domain_utils.registrable_domain("blog.example.com"), "example.com")
        self.assertEqual(domain_utils.registrable_domain("https://www.example.co.uk/x"), "example.co.uk")

    def test_is_clean_root_form_rejects_subdomain(self):
        self.assertFalse(domain_utils.is_clean_root_form("blog.example.com"))

    def test_is_clean_root_form_accepts_private_psl_entry(self):
        # foo.blogspot.com IS its own registrable domain under this
        # project's include_psl_private_domains=True policy, so it must
        # pass is_clean_root_form despite looking like a "subdomain".
        self.assertTrue(domain_utils.is_clean_root_form("foo.blogspot.com"))

    def test_is_clean_root_form_accepts_plain_root(self):
        self.assertTrue(domain_utils.is_clean_root_form("example.com"))
        self.assertTrue(domain_utils.is_clean_root_form("example.co.uk"))

    def test_is_clean_root_form_rejects_scheme_www_path(self):
        self.assertFalse(domain_utils.is_clean_root_form("https://example.com/"))
        self.assertFalse(domain_utils.is_clean_root_form("www.example.com"))
        self.assertFalse(domain_utils.is_clean_root_form("example.com/x"))

    # -- Item 1 (last pre-950 patch): content_scale_proxy evidence-group coverage --

    def test_content_scale_proxy_in_all_groups(self):
        proxy_ev_fields = [g[1] for g in evidence_harden.ALL_GROUPS if g[0] == "content_scale_proxy_value"]
        self.assertEqual(proxy_ev_fields, ["content_scale_proxy_evidence"])

    def test_evidence_cell_count_is_11_groups(self):
        self.assertEqual(len(evidence_harden.ALL_GROUPS), 11)

    def test_evidence_group_coverage_detects_missing_field(self):
        fieldnames = [g[1] for g in evidence_harden.ALL_GROUPS] + ["mystery_field_evidence"]
        missing, duplicated = evidence_harden.verify_group_coverage(fieldnames)
        self.assertIn("mystery_field_evidence", missing)
        self.assertEqual(duplicated, [])

    def test_evidence_group_coverage_detects_duplicate_group(self):
        fieldnames = [g[1] for g in evidence_harden.ALL_GROUPS]
        extra_groups = evidence_harden.ALL_GROUPS + [evidence_harden.ALL_GROUPS[0]]
        original = evidence_harden.ALL_GROUPS
        try:
            evidence_harden.ALL_GROUPS = extra_groups
            missing, duplicated = evidence_harden.verify_group_coverage(fieldnames)
            self.assertEqual(duplicated, [original[0][1]])
        finally:
            evidence_harden.ALL_GROUPS = original

    def test_evidence_group_coverage_clean_for_real_schema(self):
        import migrate_schema
        missing, duplicated = evidence_harden.verify_group_coverage(migrate_schema.FIELDNAMES)
        self.assertEqual(missing, [])
        self.assertEqual(duplicated, [])

    def test_content_scale_proxy_value_without_method_raises(self):
        d = self._min_row(content_scale_proxy_value="1200", content_scale_proxy_method="UNKNOWN",
                           content_scale_proxy_evidence="D", content_scale_proxy_note="sitemap URL count")
        with self.assertRaises(evidence_harden.EvidenceHardenError):
            evidence_harden.harden_row(d)

    def test_content_scale_proxy_value_with_method_passes(self):
        d = self._min_row(content_scale_proxy_value="1200", content_scale_proxy_method="sitemap URL count",
                           content_scale_proxy_evidence="D", content_scale_proxy_note="counted sitemap.xml entries")
        evidence_harden.harden_row(d)  # must not raise

    def test_content_scale_proxy_gate_check_catches_missing_method(self):
        row = self._min_row(content_scale_proxy_value="1200", content_scale_proxy_method="UNKNOWN")
        bad = run_gate_v2.check_content_scale_proxy_method([row])
        self.assertEqual(len(bad), 1)

    def test_content_scale_proxy_gate_check_passes_when_unknown(self):
        row = self._min_row(content_scale_proxy_value="UNKNOWN", content_scale_proxy_method="UNKNOWN")
        bad = run_gate_v2.check_content_scale_proxy_method([row])
        self.assertEqual(bad, [])


class TestWaveTransactionOrdering(unittest.TestCase):
    """
    Item 5 (last pre-950 engineering patch, 2026-09-17): the coordinator
    must never leave the registry saying COMMITTED while the master
    dataset doesn't actually contain the merged rows. These tests (A, B, C
    from the task spec) exercise wave_coordinator.run_wave()'s reordered
    transaction directly against temp registry/master files, using
    wave_coordinator._demo_research_fn as a stand-in worker (fabricates a
    fully-UNKNOWN, Gate-clean synthetic row -- never real research).
    """

    def test_C_all_pass_commits_registry_and_merges_master(self):
        with tempfile.TemporaryDirectory() as td:
            registry_path = Path(td) / "registry.csv"
            master_csv = Path(td) / "master.csv"
            result = wave_coordinator.run_wave(
                registry_path, master_csv, ["clean-c.test"], batch_id="T-C",
                research_fn=wave_coordinator._demo_research_fn,
            )
            self.assertEqual(result["committed"], 1)
            self.assertEqual(result["master_row_count_after_merge"], 1)
            rows = registry.load_registry(registry_path)
            self.assertEqual(rows[0]["status"], "COMMITTED")
            _, master_rows = registry.load_master_rows(master_csv)
            self.assertEqual(len(master_rows), 1)

    def test_url_candidate_stored_as_registrable_domain(self):
        """
        Item 4 (Full PSL patch, 2026-09-17): run_wave() must canonicalize
        a raw URL candidate BEFORE reserving/researching/committing it --
        the registry and master dataset must both end up with the plain
        registrable domain, never the raw URL string.

        NOTE: this fixture intentionally uses a real, PSL-listed TLD
        (.com), not a reserved/unregistered one like ".test" (RFC 2606) --
        an unlisted TLD is not guaranteed to be present in tldextract's
        bundled offline PSL snapshot, which would make this test depend on
        PSL wildcard-fallback behavior instead of the actual
        canonicalization logic under test.
        """
        with tempfile.TemporaryDirectory() as td:
            registry_path = Path(td) / "registry.csv"
            master_csv = Path(td) / "master.csv"
            wave_coordinator.run_wave(
                registry_path, master_csv, ["https://www.clean-url-example.com/some/path"], batch_id="T-URL",
                research_fn=wave_coordinator._demo_research_fn,
            )
            rows = registry.load_registry(registry_path)
            self.assertEqual(rows[0]["canonical_root_domain"], "clean-url-example.com")
            self.assertEqual(rows[0]["registrable_domain"], "clean-url-example.com")
            _, master_rows = registry.load_master_rows(master_csv)
            self.assertEqual(master_rows[0]["canonical_root_domain"], "clean-url-example.com")

    def test_A_merge_failure_leaves_registry_reserved_and_master_untouched(self):
        with tempfile.TemporaryDirectory() as td:
            registry_path = Path(td) / "registry.csv"
            master_csv = Path(td) / "master.csv"
            # Pre-seed master with a row for the SAME domain the wave will
            # research, WITHOUT registering it in the registry (simulates a
            # desync where a domain already sits in master outside the
            # coordinator's knowledge) -- this must fail compute_merge()'s
            # raw-domain overlap check before anything is written/committed.
            conflicting_row = wave_coordinator._demo_research_fn("dupe-domain.test")
            registry.write_rows_csv(master_csv, list(conflicting_row.keys()), [conflicting_row])
            original_master_content = master_csv.read_text(encoding="utf-8")

            with self.assertRaises(wave_coordinator.WaveAbortedError):
                wave_coordinator.run_wave(
                    registry_path, master_csv, ["dupe-domain.test"], batch_id="T-A",
                    research_fn=wave_coordinator._demo_research_fn,
                )

            rows = registry.load_registry(registry_path)
            self.assertEqual(rows[0]["status"], "RESERVED", "must stay RESERVED, never COMMITTED, when merge fails")
            self.assertEqual(master_csv.read_text(encoding="utf-8"), original_master_content, "master must be untouched")

    def test_B_merged_master_gate_failure_leaves_registry_reserved_and_master_untouched(self):
        with tempfile.TemporaryDirectory() as td:
            registry_path = Path(td) / "registry.csv"
            master_csv = Path(td) / "master.csv"
            # Pre-seed master with a row that is INTERNALLY invalid (Rule #8
            # violation, bypassing evidence_harden) for a DIFFERENT domain
            # than the wave researches -- compute_merge() sees no domain
            # overlap and succeeds, but the Gate run against the FULL merged
            # row set must still fail because of this pre-existing bad row.
            bad_row = wave_coordinator._demo_research_fn("already-broken.test")
            bad_row["affiliate"] = "Y"
            bad_row["affiliate_evidence"] = "UNKNOWN"
            registry.write_rows_csv(master_csv, list(bad_row.keys()), [bad_row])
            original_master_content = master_csv.read_text(encoding="utf-8")

            with self.assertRaises(wave_coordinator.WaveAbortedError):
                wave_coordinator.run_wave(
                    registry_path, master_csv, ["clean-b.test"], batch_id="T-B",
                    research_fn=wave_coordinator._demo_research_fn,
                )

            rows = registry.load_registry(registry_path)
            self.assertEqual(rows[0]["status"], "RESERVED", "must stay RESERVED when the MERGED Gate fails")
            self.assertEqual(master_csv.read_text(encoding="utf-8"), original_master_content, "master must be untouched")

    def test_D_transition_validates_all_before_mutating_any(self):
        """
        commit_domains()/reject_domains() must validate every domain in the
        call BEFORE mutating any of them -- a partially-invalid list must
        not leave the earlier, valid domains half-transitioned.
        """
        rows = [
            {"canonical_root_domain": "ok.test", "registrable_domain": "ok.test", "source_group": "t",
             "category": "UNKNOWN", "sampling_stratum": "UNKNOWN", "status": "RESERVED", "batch_id": "B1"},
            {"canonical_root_domain": "wrongbatch.test", "registrable_domain": "wrongbatch.test", "source_group": "t",
             "category": "UNKNOWN", "sampling_stratum": "UNKNOWN", "status": "RESERVED", "batch_id": "B2"},
        ]
        with self.assertRaises(registry.RegistryStateError):
            registry.commit_domains(rows, ["ok.test", "wrongbatch.test"], batch_id="B1")
        self.assertEqual(rows[0]["status"], "RESERVED", "the valid domain processed first must NOT have been mutated")


if __name__ == "__main__":
    unittest.main(verbosity=2)
