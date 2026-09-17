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

Sequence `run_wave()` performs:
    1. candidate_selection   -- caller supplies a list of candidate domains
    2. canonicalization      -- domain_utils.registrable_domain()
    3. duplicate_check       -- check_duplicate() against the registry
    4. RESERVE               -- reserve_domains(), status=RESERVED
    5. worker dispatch       -- caller-supplied `research_fn(domain) -> row dict`
                                 is called once per successfully reserved domain
                                 (in this round, `research_fn` is never wired to
                                 real research -- see --demo for a stub)
    6. wave Gate             -- run_gate_v2.run_gate() against the wave's own rows
    7. COMMIT or REJECT      -- commit_domains() on Gate PASS, reject_domains()
                                 on Gate FAIL (registry rows only; a FAILed
                                 wave's rows are never merged into the master)
    8. merge                 -- merge_wave_into_master() appends committed rows
                                 into the master Study A dataset CSV
"""

import argparse
import csv
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_domain_registry as registry  # noqa: E402
import run_gate_v2  # noqa: E402


class WaveAbortedError(RuntimeError):
    """Raised when a wave's Gate fails; the caller's registry/master files are left untouched by commit/merge."""


def run_wave(registry_path: Path, master_csv: Path, candidates: list, batch_id: str, research_fn):
    """
    Run one coordinator-only wave. `research_fn(domain: str) -> dict` must
    return a fully-populated Protocol V2 row (all of migrate_schema.FIELDNAMES)
    for that one domain -- this function does not itself perform research.

    Returns a summary dict. Raises WaveAbortedError if the wave's Gate
    fails (nothing is committed or merged in that case, though the
    RESERVED rows remain RESERVED, not silently REJECTED, since a Gate
    failure may be fixable and re-attempted under the same batch_id).
    """
    rows = registry.load_registry(registry_path)

    # 2-3: canonicalize + duplicate-check every candidate before reserving any of them.
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
        # Leave the domains RESERVED (not REJECTED) -- a failed wave is
        # usually a fixable data problem, and REJECTED should mean "this
        # domain itself was rejected", not "the wave's data had a bug".
        raise WaveAbortedError(
            "Wave Gate FAILED -- domains remain RESERVED (not committed, not rejected). "
            "Fix the data and re-run the wave under the same batch_id, or explicitly "
            "reject_domains() the ones that are genuinely bad.\n" + "\n".join(report_lines)
        )

    # 7: commit.
    rows = registry.commit_domains(rows, to_reserve, batch_id=batch_id)
    registry.save_registry(registry_path, rows)

    # 8: merge into the master dataset.
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="", encoding="utf-8") as tmp:
        writer = csv.DictWriter(tmp, fieldnames=list(wave_rows[0].keys()))
        writer.writeheader()
        for r in wave_rows:
            writer.writerow(r)
        wave_csv_path = Path(tmp.name)
    try:
        merged_count = registry.merge_wave_into_master(wave_csv_path, master_csv)
    finally:
        wave_csv_path.unlink(missing_ok=True)

    return {
        "batch_id": batch_id,
        "reserved": len(to_reserve),
        "committed": len(to_reserve),
        "master_row_count_after_merge": merged_count,
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
