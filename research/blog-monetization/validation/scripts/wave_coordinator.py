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

Production two-phase CLI (Study A wave, 2026-09-17, GPT-approved production
expansion, Section A)
--------------------------------------------------------------------------
`run_wave()` above is in-process only -- it requires a `research_fn`
callback and was only ever exercised against synthetic/demo data. Real
Study A research happens out-of-process (a person or a parallel research
agent working from a CSV of already-RESERVED domains), so this module also
exposes a two-phase CLI that splits `run_wave()`'s sequence at the
research-dispatch boundary:

    python wave_coordinator.py prepare  --registry ... --candidates ... --batch-id ... --reserved-out ...
    python wave_coordinator.py finalize --registry ... --master ...    --batch-id ... --research-csv ...

`prepare` performs steps 1-4 above (canonicalize, duplicate-check,
RESERVE) and writes out exactly which domains got reserved -- it never
performs research and never touches the master dataset file. Unlike
`run_wave()`, it does NOT abort on a bad candidate (invalid/duplicate/
already-registered); it reports each one back so the caller can swap in a
replacement candidate and re-run `prepare` under the same --batch-id.

`finalize` performs steps 5-10 above given a `research-csv` of already-
completed research rows: it verifies the research CSV's domain set
matches the RESERVED set for --batch-id exactly (no silent gaps or
extras), verifies every row has exactly the Protocol V2 65-column schema,
Gates the wave alone, Gates the wave merged into the current master (in
memory), and only if both pass writes the master file and commits the
registry -- the same "never COMMIT before the master write succeeds"
ordering as `run_wave()`, so any failure leaves the registry RESERVED and
the master file untouched.

A worker/research agent given a `prepare`-produced reserved-domains CSV
never touches the registry directly, exactly as the coordinator-only
architecture above requires -- it only writes `research_results.csv` for
`finalize` to read.
"""

import argparse
import csv
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


def prepare_wave(registry_path: Path, candidates: list, batch_id: str) -> dict:
    """
    Phase 1 of the two-phase PRODUCTION CLI (Study A wave, 2026-09-17,
    GPT-approved production expansion, Section A). Unlike `run_wave()`
    (which is in-process and requires a `research_fn` callback, and was
    only ever exercised with synthetic/demo data), `prepare_wave()` is
    meant to be called from the `prepare` CLI subcommand, run BEFORE any
    real web research happens, so that the coordinator -- not a research
    worker -- is the only thing that ever writes RESERVED rows to the
    registry.

    Unlike `run_wave()`, this function is TOLERANT of bad candidates: an
    unrecognized/invalid domain, a within-batch duplicate, or a domain
    already present in the registry under any status does NOT abort the
    whole call -- it's reported back so the caller can pick replacement
    candidates and re-run `prepare` (this matches the "회전 배분/대체"
    workflow described in the round's instructions, where a rejected
    candidate is swapped for another one, not treated as a hard failure).

    Never touches research results or the master dataset file.

    Returns:
        {
          "batch_id": str,
          "reserved_rows": [registry row dict, ...]   # newly RESERVED under batch_id
          "invalid": [(raw_candidate, reason), ...],
          "already_taken": [(raw_candidate, registrable_domain, existing_status), ...],
          "duplicate_within_batch": [(raw_candidate, registrable_domain, first_raw_candidate), ...],
        }
    """
    rows = registry.load_registry(registry_path)
    idx = registry.registry_index(rows)

    invalid = []
    seen_canon = {}
    duplicate_within_batch = []
    already_taken = []
    to_reserve_raw = []

    for c in candidates:
        canon = domain_utils.registrable_domain(c)
        if not canon:
            invalid.append((c, "failed to canonicalize to a non-empty registrable domain"))
            continue
        if canon in seen_canon:
            duplicate_within_batch.append((c, canon, seen_canon[canon]))
            continue
        seen_canon[canon] = c
        existing = idx.get(canon)
        if existing is not None:
            already_taken.append((c, canon, existing["status"]))
            continue
        to_reserve_raw.append(c)

    rows, dupes = registry.reserve_domains(rows, to_reserve_raw, batch_id=batch_id,
                                            source_group="Study A production wave")
    assert not dupes, f"Unexpected dupes after prepare_wave's own pre-filtering: {dupes}"
    registry.save_registry(registry_path, rows)

    reserved_rows = [r for r in rows if r["batch_id"] == batch_id and r["status"] == "RESERVED"]

    return {
        "batch_id": batch_id,
        "reserved_rows": reserved_rows,
        "invalid": invalid,
        "already_taken": already_taken,
        "duplicate_within_batch": duplicate_within_batch,
    }


def finalize_wave(registry_path: Path, master_csv: Path, batch_id: str, research_rows: list) -> dict:
    """
    Phase 2 of the two-phase PRODUCTION CLI (Study A wave, 2026-09-17,
    Section A). Called from the `finalize` CLI subcommand, AFTER real web
    research has produced full Protocol V2 rows for every domain that
    `prepare_wave()` reserved under `batch_id`.

    Enforces, in order (raising WaveAbortedError -- and leaving the
    registry at RESERVED and the master file untouched -- on the first
    failure):
        1. every domain RESERVED under batch_id has a matching research
           row, and every research row's domain was actually reserved
           under this batch_id (no silent extras, no silent gaps);
        2. every research row uses exactly the Protocol V2 65-column
           schema (migrate_schema.FIELDNAMES) -- no missing/extra columns;
        3. the wave's own rows pass the Gate on their own;
        4. the wave merges cleanly (column match, no raw/registrable
           domain overlap) against the CURRENT on-disk master, in memory
           only;
        5. the FULL merged row set (existing master + this wave) also
           passes the Gate.
    Only if all five pass does this function write the merged master file
    and then flip the registry rows from RESERVED to COMMITTED -- the same
    "never COMMIT before the master write succeeds" ordering as
    `run_wave()` above, for the same reason (a Gate/merge failure must
    always leave the SAFE state: RESERVED, master unchanged).
    """
    rows = registry.load_registry(registry_path)
    reserved_rows = [r for r in rows if r["batch_id"] == batch_id and r["status"] == "RESERVED"]
    if not reserved_rows:
        raise WaveAbortedError(
            f"No RESERVED rows found for batch_id={batch_id!r} -- run the `prepare` subcommand first."
        )
    reserved_domains = {r["registrable_domain"] for r in reserved_rows}

    research_domains = set()
    for r in research_rows:
        raw = r.get("canonical_root_domain", "")
        research_domains.add(domain_utils.registrable_domain(raw))

    missing = reserved_domains - research_domains
    extra = research_domains - reserved_domains
    if missing or extra:
        raise WaveAbortedError(
            f"research_results domain set does not match the RESERVED set for batch_id={batch_id!r}. "
            f"Missing (reserved but not researched): {sorted(missing)}. "
            f"Extra (researched but not reserved under this batch_id): {sorted(extra)}. "
            f"Fix research_results.csv (or re-run `prepare`) before retrying `finalize`."
        )

    import migrate_schema
    expected_fields = set(migrate_schema.FIELDNAMES)
    for i, r in enumerate(research_rows):
        actual_fields = set(r.keys())
        if actual_fields != expected_fields:
            raise WaveAbortedError(
                f"research_results.csv row {i} (domain={r.get('canonical_root_domain')!r}) does not match "
                f"the Protocol V2 65-column schema. Missing columns: {sorted(expected_fields - actual_fields)}. "
                f"Unexpected columns: {sorted(actual_fields - expected_fields)}."
            )

    report_lines, all_passed = run_gate_v2.run_gate(research_rows)
    if not all_passed:
        raise WaveAbortedError(
            f"Wave Gate FAILED for batch_id={batch_id!r} -- domains remain RESERVED (not committed, not "
            f"rejected), master file NOT touched. Fix the data and re-run `finalize` under the same "
            f"batch_id.\n" + "\n".join(report_lines)
        )

    existing_fieldnames, existing_rows = registry.load_master_rows(master_csv)
    try:
        merged_fieldnames, merged_rows = registry.compute_merge(
            existing_fieldnames, existing_rows, list(research_rows[0].keys()), research_rows
        )
    except ValueError as e:
        raise WaveAbortedError(
            f"batch_id={batch_id!r}: pre-merge validation against the current master failed -- domains "
            f"remain RESERVED, master file NOT touched: {e}"
        )

    merged_report_lines, merged_all_passed = run_gate_v2.run_gate(merged_rows)
    if not merged_all_passed:
        raise WaveAbortedError(
            f"batch_id={batch_id!r}: merged-master Gate FAILED after adding this wave's rows -- master "
            f"file was NOT written, domains remain RESERVED.\n" + "\n".join(merged_report_lines)
        )

    registry.write_rows_csv(master_csv, merged_fieldnames, merged_rows)

    domains_to_commit = [r["canonical_root_domain"] for r in reserved_rows]
    rows = registry.commit_domains(rows, domains_to_commit, batch_id=batch_id)
    registry.save_registry(registry_path, rows)

    status_counts = {}
    for r in rows:
        status_counts[r["status"]] = status_counts.get(r["status"], 0) + 1

    return {
        "batch_id": batch_id,
        "committed": len(domains_to_commit),
        "master_row_count_after_merge": len(merged_rows),
        "registry_status_distribution": status_counts,
    }


def _read_candidates_csv(path: Path, column: str = "candidate") -> list:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if column not in (reader.fieldnames or []):
            raise SystemExit(
                f"Candidate CSV {path} has no column named {column!r} (found: {reader.fieldnames}). "
                f"Pass --column to use a different header."
            )
        return [row[column].strip() for row in reader if row[column].strip()]


def _write_reserved_csv(path: Path, reserved_rows: list):
    registry.write_rows_csv(path, registry.REGISTRY_FIELDNAMES, reserved_rows)


def _cmd_prepare(args) -> int:
    registry_path = Path(args.registry)
    candidates_path = Path(args.candidates)
    reserved_out = Path(args.reserved_out)

    candidates = _read_candidates_csv(candidates_path, column=args.column)
    result = prepare_wave(registry_path, candidates, batch_id=args.batch_id)
    _write_reserved_csv(reserved_out, result["reserved_rows"])

    print(f"[prepare] batch_id={result['batch_id']!r}")
    print(f"[prepare] candidates read: {len(candidates)}")
    print(f"[prepare] newly RESERVED: {len(result['reserved_rows'])} -> {reserved_out}")
    if result["invalid"]:
        print(f"[prepare] INVALID (could not canonicalize), {len(result['invalid'])}:")
        for c, reason in result["invalid"]:
            print(f"    {c!r}: {reason}")
    if result["duplicate_within_batch"]:
        print(f"[prepare] DUPLICATE within this candidate list, {len(result['duplicate_within_batch'])}:")
        for c, canon, first in result["duplicate_within_batch"]:
            print(f"    {c!r} -> {canon} (already seen as {first!r} earlier in this same file)")
    if result["already_taken"]:
        print(f"[prepare] ALREADY IN REGISTRY (rejected), {len(result['already_taken'])}:")
        for c, canon, status in result["already_taken"]:
            print(f"    {c!r} -> {canon} (status={status})")
    print(
        f"[prepare] Reserved {len(result['reserved_rows'])} of {len(candidates)} candidates. "
        f"Replace the rejected ones and re-run `prepare` with the same --batch-id if you need more."
    )
    return 0


def _cmd_finalize(args) -> int:
    registry_path = Path(args.registry)
    master_csv = Path(args.master)
    research_csv = Path(args.research_csv)

    with open(research_csv, newline="", encoding="utf-8") as f:
        research_rows = list(csv.DictReader(f))
    if not research_rows:
        print(f"[finalize] research_csv {research_csv} has no rows.", file=sys.stderr)
        return 1

    try:
        result = finalize_wave(registry_path, master_csv, batch_id=args.batch_id, research_rows=research_rows)
    except WaveAbortedError as e:
        print(f"[finalize] ABORTED: {e}", file=sys.stderr)
        return 1

    summary_lines = [
        f"batch_id: {result['batch_id']}",
        f"committed: {result['committed']}",
        f"master_row_count_after_merge: {result['master_row_count_after_merge']}",
        f"registry_status_distribution: {result['registry_status_distribution']}",
    ]
    summary_text = "\n".join(summary_lines) + "\n"
    print("[finalize] SUCCESS")
    print(summary_text)
    if args.summary_out:
        Path(args.summary_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.summary_out).write_text(summary_text, encoding="utf-8")
        print(f"[finalize] wrote summary to {args.summary_out}")
    return 0


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
    parser.add_argument("--demo", action="store_true",
                         help="(legacy top-level flag, still supported) Run the synthetic-domain "
                              "self-test -- equivalent to the `demo` subcommand.")
    subparsers = parser.add_subparsers(dest="command")

    p_demo = subparsers.add_parser("demo", help="Synthetic-domain self-test (no real registry/master touched).")
    p_demo.set_defaults(func=lambda args: run_demo())

    p_prepare = subparsers.add_parser(
        "prepare",
        help="Phase 1 of a real production wave: canonicalize + duplicate-check candidates and "
             "RESERVE the clean ones. Performs NO research and never touches the master dataset.",
    )
    p_prepare.add_argument("--registry", required=True, help="Path to domain_registry.csv.")
    p_prepare.add_argument("--candidates", required=True,
                            help="CSV of raw candidate domains/URLs (one column, header configurable via --column).")
    p_prepare.add_argument("--column", default="candidate", help="Candidate CSV column name (default: candidate).")
    p_prepare.add_argument("--batch-id", required=True, help="Batch id for this wave, e.g. STUDY-A-W001.")
    p_prepare.add_argument("--reserved-out", required=True,
                            help="Where to write the registry rows that were actually RESERVED.")
    p_prepare.set_defaults(func=_cmd_prepare)

    p_finalize = subparsers.add_parser(
        "finalize",
        help="Phase 2 of a real production wave: verify research_results.csv against the RESERVED "
             "set for --batch-id, Gate it (alone, then merged into the master), and only then write "
             "the master file and flip the registry to COMMITTED.",
    )
    p_finalize.add_argument("--registry", required=True, help="Path to domain_registry.csv.")
    p_finalize.add_argument("--master", required=True, help="Path to the Study A cumulative master CSV.")
    p_finalize.add_argument("--batch-id", required=True, help="Batch id this research was reserved under.")
    p_finalize.add_argument("--research-csv", required=True,
                             help="Fully-populated Protocol V2 (65-column) research results CSV for this batch.")
    p_finalize.add_argument("--summary-out", default=None, help="Optional path to write a short text summary to.")
    p_finalize.set_defaults(func=_cmd_finalize)

    args = parser.parse_args()

    if args.command is None:
        if args.demo:
            return run_demo()
        print("Run one of: `demo` (synthetic self-test), `prepare` (reserve candidates for a real "
              "wave), or `finalize` (Gate + commit a real wave's research results). See --help.",
              file=sys.stderr)
        return 1
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
