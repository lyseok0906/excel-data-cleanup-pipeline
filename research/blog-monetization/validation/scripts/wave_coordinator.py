#!/usr/bin/env python3
"""
Single-coordinator wave orchestrator for future 950-site expansion waves
(GPT follow-up to commit 8dffb08, 2026-09-17, Item 4).

This is a REUSABLE TOOL, not a one-shot script for this round: it defines
`run_wave()`, which a future session calls once actual research is
approved, and a `--demo` CLI mode that exercises the full state machine
end-to-end against SYNTHETIC placeholder domains (never real sites) in a
temporary registry file, so the mechanics can be verified without
performing any new research and without touching the real
research/blog-monetization/registry/domain_registry.csv.

Per this round's explicit constraint ("아직 실제 950 research는 실행하지
않는다"), running this file directly (`python wave_coordinator.py --demo`)
is the ONLY thing it does in this round -- it does not reserve, research,
or commit any real domain.

Coordinator-only architecture: only this module is expected to call
reserve_domains/commit_domains/reject_domains/merge_wave_into_master.
A parallel research worker (a subagent, a separate script, a person)
receives a list of already-RESERVED domains to research and hands back
plain research rows; it never touches the registry file itself. This is
what prevents two workers from racing to reserve the same domain.

Sequence `run_wave()` performs (REORDERED in the last pre-950 engineering
patch, 2026-09-17, commit 8dffb08 GPT follow-up, Item 5 -- see the
docstring note above run_wave() below for why):
    1. candidate_selection   -- caller supplies a list of candidate domains
    2. canonicalization      -- domain_utils.registrable_domain() (ACTUALLY applied to every
                                 candidate as of the Full PSL patch, 2026-09-17, Item 4 --
                                 previously this step was documented here but not implemented:
                                 raw candidate strings were reserved/researched/committed
                                 verbatim. A candidate that fails to canonicalize aborts the
                                 whole wave before any reservation or research happens.)
    3. duplicate_check       -- check_duplicate() against the registry, using the
                                 now-canonical domain
    4. RESERVE               -- reserve_domains(), status=RESERVED
    5. worker dispatch       -- caller-supplied `research_fn(domain) -> row dict`
                                 is called once per successfully reserved domain
                                 (in this round, `research_fn` is never wired to
                                 real research -- see --demo for a stub)
    6. wave Gate             -- run_gate_v2.run_gate() against the wave's own rows
    7. merge validation      -- build_domain_registry.compute_merge() against the
                                 CURRENT on-disk master, in memory only (no write yet)
    8. merged-master Gate    -- run_gate_v2.run_gate() against the FULL merged
                                 row set (existing master + this wave), not just
                                 the wave's own rows
    9. master write          -- ONLY if both Gates (6 and 8) passed: write the
                                 merged rows to the master CSV
   10. COMMIT                -- ONLY after the master write succeeds: commit_domains()
                                 flips the reserved domains to COMMITTED and saves
                                 the registry. A Gate failure at 6 or 8 raises
                                 WaveAbortedError and leaves the domains RESERVED
                                 (not committed, not rejected, master untouched).
"""

import argparse
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_domain_registry as registry  # noqa: E402
import domain_utils  # noqa: E402
import run_gate_v2  # noqa: E402


class WaveAbortedError(RuntimeError):
    """Raised when a wave's Gate fails; the caller's registry/master files are left untouched by commit/merge."""


def run_wave(registry_path: Path, master_csv: Path, candidates: list, batch_id: str, research_fn):
    """
    Run one coordinator-only wave. `research_fn(domain: str) -> dict` must
    return a fully-populated Protocol V2 row (all of migrate_schema.FIELDNAMES)
    for that one domain -- this function does not itself perform research.

    Returns a summary dict. Raises WaveAbortedError if either Gate fails
    (the wave's own rows, or the full merged master after adding them) --
    in both cases nothing is committed and the master file is NOT written,
    and the RESERVED rows remain RESERVED, not silently REJECTED, since a
    Gate failure may be fixable and re-attempted under the same batch_id.

    Transaction ordering (Item 5, last pre-950 engineering patch,
    2026-09-17, commit 8dffb08 GPT follow-up): the PREVIOUS version wrote
    registry status=COMMITTED before merging into the master file. If the
    merge then failed (column mismatch, a duplicate the wave-only Gate
    couldn't see, a crash), the registry would claim a domain was
    COMMITTED while the master dataset never actually gained that row --
    an inconsistent state with no clean recovery. This version reorders
    the irreversible steps so failure always leaves the SAFE state
    (RESERVED, master unchanged) rather than the UNSAFE one (COMMITTED,
    master unchanged): wave Gate -> validate the merge in memory (no
    write) -> Gate the FULL merged row set -> only then write the master
    file -> only then flip the registry to COMMITTED.
    """
    rows = registry.load_registry(registry_path)

    # 2: canonicalize EVERY candidate BEFORE it ever reaches the registry
    # (Full PSL patch, 2026-09-17): a raw candidate like
    # "https://www.example.com/path" must never be stored as
    # canonical_root_domain verbatim -- only "example.com" is reserved,
    # researched, and committed. Any candidate that fails to canonicalize
    # to a non-empty registrable domain aborts the WHOLE wave before any
    # research is dispatched (never silently skipped).
    invalid = []
    canonicalized = []
    for c in candidates:
        canon = domain_utils.registrable_domain(c)
        if not canon:
            invalid.append(c)
        else:
            canonicalized.append(canon)
    if invalid:
        raise WaveAbortedError(
            f"{len(invalid)} candidate(s) could not be canonicalized to a non-empty registrable "
            f"domain -- aborting before any research or reservation: {invalid}"
        )
    # De-duplicate WITHIN this candidate list itself: two raw strings that
    # canonicalize to the SAME registrable domain (e.g. "example.com" and
    # "https://www.example.com/") must not both be reserved/researched.
    seen = set()
    candidates = []
    for c in canonicalized:
        if c not in seen:
            seen.add(c)
            candidates.append(c)

    # 3: duplicate-check every (now-canonical) candidate against the
    # registry before reserving any of them.
    already_taken = []
    to_reserve = []
    for c in candidates:
        status = registry.check_duplicate(c, rows)
        if status is not None:
            already_taken.append((c, status))
        else:
            to_reserve.append(c)
    if already_taken:
        raise WaveAbortedError(
            f"{len(already_taken)} candidate(s) already present in the registry, refusing to "
            f"start the wave until the candidate list is cleaned up: {already_taken}"
        )

    # 4: reserve.
    rows, dupes = registry.reserve_domains(rows, to_reserve, batch_id=batch_id)
    assert not dupes, f"Unexpected dupes after a clean duplicate-check pass: {dupes}"
    registry.save_registry(registry_path, rows)

    # 5: dispatch to the (caller-supplied) worker, one domain at a time.
    wave_rows = [research_fn(d) for d in to_reserve]

    # 6: wave Gate, against ONLY this wave's own rows (a wave must stand on its own).
    report_lines, all_passed = run_gate_v2.run_gate(wave_rows)
    if not all_passed:
        raise WaveAbortedError(
            "Wave Gate FAILED -- domains remain RESERVED (not committed, not rejected), master file "
            "NOT touched. Fix the data and re-run the wave under the same batch_id, or explicitly "
            "reject_domains() the ones that are genuinely bad.\n" + "\n".join(report_lines)
        )

    # 7: validate the merge AGAINST THE CURRENT ON-DISK MASTER, in memory
    # only -- no write happens here. A column-mismatch or a duplicate the
    # wave-only Gate above couldn't see (e.g. against rows already in the
    # master from a prior wave) raises here and aborts before anything is
    # written or committed.
    existing_fieldnames, existing_rows = registry.load_master_rows(master_csv)
    try:
        merged_fieldnames, merged_rows = registry.compute_merge(
            existing_fieldnames, existing_rows, list(wave_rows[0].keys()), wave_rows
        )
    except ValueError as e:
        raise WaveAbortedError(
            f"Wave rows failed pre-merge validation against the current master -- domains remain "
            f"RESERVED, master file NOT touched: {e}"
        )

    # 8: Gate the FULL merged row set (existing master + this wave), not
    # just the wave's own rows -- a wave can be internally clean and still
    # make the overall dataset inconsistent (Test B in
    # test_validation_tooling.py exercises exactly this).
    merged_report_lines, merged_all_passed = run_gate_v2.run_gate(merged_rows)
    if not merged_all_passed:
        raise WaveAbortedError(
            "Merged-master Gate FAILED after adding this wave's rows -- master file was NOT written, "
            "domains remain RESERVED (not committed, not rejected).\n" + "\n".join(merged_report_lines)
        )

    # 9: only now -- after BOTH gates passed -- write the master file.
    registry.write_rows_csv(master_csv, merged_fieldnames, merged_rows)

    # 10: only after the master write succeeded, flip the registry to COMMITTED.
    rows = registry.commit_domains(rows, to_reserve, batch_id=batch_id)
    registry.save_registry(registry_path, rows)

    return {
        "batch_id": batch_id,
        "reserved": len(to_reserve),
        "committed": len(to_reserve),
        "master_row_count_after_merge": len(merged_rows),
    }


def _demo_research_fn(domain: str) -> dict:
    """
    STUB ONLY -- fabricates a minimally-valid Protocol V2 row for a
    SYNTHETIC placeholder domain (example-*.test, never resolvable, never
    a real site) purely to exercise the state machine. This is not real
    research and must never be pointed at a real domain.
    """
    import migrate_schema
    import schema_extend

    row = {f: "UNKNOWN" for f in migrate_schema.FIELDNAMES}
    row.update({
        "canonical_root_domain": domain,
        "site_name": f"Demo site for {domain}",
        "primary_niche": "Demo/placeholder row for wave_coordinator.py --demo",
        "category": schema_extend.CATEGORY_ENUM[0],
        "sub_category": "UNKNOWN",
        "as_of_date": "2026-09-17",
        "sampling_stratum": "Mid-scale Active Site",
        "traffic_tier": "UNKNOWN",
        "contrast_pattern": "NOT_APPLICABLE",
        "contrast_evidence_period": "",
        "traffic_scope": "CONTENT_ONLY",
        "traffic_provider": "UNKNOWN",
        "traffic_metric": "UNKNOWN",
    })
    for f in ["is_niche_authority", "is_contrast_case", "display_ads", "affiliate",
              "own_product", "course_or_community", "newsletter_email_capture"]:
        row[f] = "UNKNOWN"
        row[f + "_evidence"] = "UNKNOWN"
        row[f + "_source_url"] = "UNKNOWN"
        row[f + "_note"] = ""
    return row


def run_demo():
    """Self-contained demo against synthetic placeholder domains and a throwaway temp registry/master."""
    with tempfile.TemporaryDirectory() as td:
        registry_path = Path(td) / "demo_registry.csv"
        master_csv = Path(td) / "demo_master.csv"
        candidates = ["example-demo-a.test", "example-demo-b.test", "example-demo-c.test"]

        print(f"[demo] Running a 3-site synthetic wave (batch_id=DEMO-WAVE-1) against a temp registry at {registry_path}")
        result = run_wave(registry_path, master_csv, candidates, batch_id="DEMO-WAVE-1", research_fn=_demo_research_fn)
        print(f"[demo] Wave 1 result: {result}")

        rows = registry.load_registry(registry_path)
        assert all(r["status"] == "COMMITTED" for r in rows), "All demo domains should now be COMMITTED"
        print("[demo] Verified: all 3 synthetic domains are COMMITTED after the wave.")

        # Prove the immutability/cross-batch guards actually raise.
        try:
            registry.commit_domains(rows, ["example-demo-a.test"], batch_id="DEMO-WAVE-1")
            raise AssertionError("Expected RegistryStateError re-committing an already-COMMITTED domain")
        except registry.RegistryStateError:
            print("[demo] Verified: re-committing an already-COMMITTED domain correctly raises RegistryStateError.")

        rows2, dupes = registry.reserve_domains(rows, ["example-demo-a.test"], batch_id="DEMO-WAVE-2")
        assert dupes == [("example-demo-a.test", "COMMITTED")]
        print("[demo] Verified: reserving an already-COMMITTED domain under a new batch is correctly refused (returned as a dupe, not silently reserved).")

        rows3, dupes3 = registry.reserve_domains(rows, ["example-demo-d.test"], batch_id="DEMO-WAVE-2")
        try:
            registry.commit_domains(rows3, ["example-demo-d.test"], batch_id="DEMO-WAVE-1")  # wrong batch_id
            raise AssertionError("Expected RegistryStateError committing with the wrong batch_id")
        except registry.RegistryStateError:
            print("[demo] Verified: committing a RESERVED domain under the WRONG batch_id correctly raises RegistryStateError.")

    print("[demo] All wave_coordinator.py state-machine demo checks passed. No real registry or master files were touched.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="Run the synthetic-domain self-test (the only supported mode this round).")
    args = parser.parse_args()
    if not args.demo:
        print("This round performs no real 950-site research. Run with --demo to verify the wave "
              "state machine against synthetic placeholder domains, or import run_wave() from a "
              "future session once real research is approved.", file=sys.stderr)
        return 1
    return run_demo()


if __name__ == "__main__":
    sys.exit(main())
