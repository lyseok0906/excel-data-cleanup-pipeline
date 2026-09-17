#!/usr/bin/env python3
"""
Domain Registry builder/tooling for the pre-950-expansion architecture
(pre-950 hardening round, 2026-09-17, Item 6).

Why this exists
----------------
Hardcoding 1000+ site rows directly into a single Python module (as
build_a0_phase2.py currently does for its 40 rows) does not scale to a
950-site expansion, and gives no cheap way to check "has any agent
already reserved/researched this domain" before starting new research on
it -- especially once multiple waves (or multiple parallel agents) are
involved.

This module defines and maintains `research/blog-monetization/registry/domain_registry.csv`,
a minimal ledger with one row per canonical root domain and a `status`
state machine:

    EXCLUDED_PRIOR_PILOT -- already used in the original 100-site pilot
                            study (research/blog-monetization-100/); must
                            never be re-selected for Study A.
    RESERVED             -- a wave has claimed this domain for research
                            but has not yet committed validated data.
    COMMITTED            -- fully researched, validated (Gate PASS), and
                            present in the current Study A dataset
                            (validation_50_v2.csv and successors).
    REJECTED             -- was reserved/considered but dropped (e.g.
                            turned out to be a duplicate, defunct beyond
                            usable evidence, or out of scope) -- kept in
                            the registry (not deleted) so it is never
                            re-reserved by mistake.

Single-coordinator architecture (GPT follow-up to commit 8dffb08, 2026-09-17,
Item 4): a parallel research WORKER never writes to the registry directly.
Only a single COORDINATOR (see wave_coordinator.py) performs the sequence
below; workers only research a domain they were handed after it was
already RESERVED, and hand validated rows back for the coordinator to
commit. This prevents two workers from racing to reserve the same domain.

Intended flow for a future 950-site wave (coordinator-only):
    candidate domain
        -> registrable_domain() canonicalization (domain_utils.py)
        -> check_duplicate() against the registry AND against every
           status (a domain EXCLUDED_PRIOR_PILOT or already COMMITTED
           or RESERVED by another wave must be skipped)
        -> reserve_domains([...], batch_id=...)   (status=RESERVED)
        -> dispatch to a worker for research, run the per-wave Gate
        -> commit_domains([...], batch_id=...)    (status=COMMITTED)
           or reject_domains([...], reason=...)   (status=REJECTED)
        -> merge_wave_into_master(...) appends the wave's validated CSV
           rows into the master Study A dataset file.

State-transition rules (enforced by commit_domains/reject_domains, not
just documented -- RegistryStateError below):
    EXCLUDED_PRIOR_PILOT -> (nothing)            immutable, always
    COMMITTED            -> (nothing)            immutable, always
    (new domain)         -> RESERVED             via reserve_domains only
    RESERVED (batch X)   -> COMMITTED/REJECTED   only by batch_id == X
    RESERVED (batch X)   -> COMMITTED/REJECTED   attempted by batch_id != X
                                                  is REJECTED with an error
                                                  (a wave can never touch
                                                  another wave's reservation)

This script does NOT perform any new site research and does NOT reserve
or commit any domains on its own. Run directly, it only (re)builds the
registry file from the CSVs that already exist in this repo (the current
50-site Study A dataset as COMMITTED). Seeding the 97 unique
EXCLUDED_PRIOR_PILOT domains from the original 100-site pilot study
(research/blog-monetization-100/sites.csv) requires that file, which is
NOT present in this workspace checkout -- see the module-level BLOCKER
note below and the pre-950 hardening report for details. Use
--pilot-csv to seed it once that file is available.
"""

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import domain_utils  # noqa: E402

REGISTRY_FIELDNAMES = [
    "canonical_root_domain",
    "registrable_domain",
    "source_group",
    "category",
    "sampling_stratum",
    "status",
    "batch_id",
]

REGISTRY_PATH = Path(__file__).parent.parent.parent / "registry" / "domain_registry.csv"

VALID_STATUSES = {"EXCLUDED_PRIOR_PILOT", "RESERVED", "COMMITTED", "REJECTED"}
IMMUTABLE_STATUSES = {"EXCLUDED_PRIOR_PILOT", "COMMITTED"}


class RegistryStateError(ValueError):
    """Raised when a commit/reject call would perform an illegal state transition."""

# NOTE (pre-950 hardening round, 2026-09-17): the original 100-site pilot
# study's domain list (research/blog-monetization/pilot-100/sites.csv in
# this repo layout -- not research/blog-monetization-100/ as first assumed)
# was not present in this session's initial workspace checkout, but was
# retrieved from the user's connected device mid-round and used to seed
# EXCLUDED_PRIOR_PILOT below. It uses the pilot study's own pre-V2 schema
# (a "domain" column, not "canonical_root_domain"), handled via the
# domain_field parameter to _seed_from_study_csv. The pilot dataset
# contains 3 domains independently sampled under two categories each
# (thespruce.com, bobvila.com, thepointsguy.com -- see the pilot study's
# methodology.md); this module collapses those to a single registry row
# per unique registrable domain (97 unique rows from 100 study rows).


def load_registry(path: Path):
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_registry(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=REGISTRY_FIELDNAMES)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def registry_index(rows):
    """registrable_domain -> row, for O(1) duplicate checks."""
    return {r["registrable_domain"]: r for r in rows}


def check_duplicate(candidate_raw: str, rows) -> str | None:
    """
    Return the existing row's status if `candidate_raw` already appears
    in the registry under any status, else None (safe to reserve).
    """
    reg_domain = domain_utils.registrable_domain(candidate_raw)
    idx = registry_index(rows)
    hit = idx.get(reg_domain)
    return hit["status"] if hit else None


def _seed_from_study_csv(csv_path: Path, source_group: str, batch_id: str, status: str, domain_field: str):
    with open(csv_path, newline="", encoding="utf-8") as f:
        study_rows = list(csv.DictReader(f))
    seeded = []
    seen_registrable = set()
    duplicate_domains = []
    for r in study_rows:
        domain = r[domain_field]
        reg = domain_utils.registrable_domain(domain)
        if reg in seen_registrable:
            # The pilot-100 study is known to contain 3 domains sampled
            # independently under two categories each (thespruce.com,
            # bobvila.com, thepointsguy.com -- see pilot-100/methodology.md);
            # only one registry row per unique registrable domain is kept.
            duplicate_domains.append(domain)
            continue
        seen_registrable.add(reg)
        seeded.append({
            "canonical_root_domain": domain,
            "registrable_domain": reg,
            "source_group": source_group,
            "category": r.get("primary_niche", "UNKNOWN"),
            "sampling_stratum": r.get("sampling_stratum", "UNKNOWN"),
            "status": status,
            "batch_id": batch_id,
        })
    if duplicate_domains:
        print(f"NOTE: {len(duplicate_domains)} duplicate domain(s) within {csv_path.name} "
              f"collapsed to a single registry row each: {duplicate_domains}", file=sys.stderr)
    return seeded


def seed_committed_from_a0(a0_csv: Path):
    return _seed_from_study_csv(a0_csv, source_group="Study A (A0)", batch_id="A0-cumulative-50",
                                 status="COMMITTED", domain_field="canonical_root_domain")


def seed_excluded_from_pilot(pilot_csv: Path):
    return _seed_from_study_csv(pilot_csv, source_group="Pilot-100", batch_id="Pilot-100",
                                 status="EXCLUDED_PRIOR_PILOT", domain_field="domain")


def reserve_domains(rows, candidates, batch_id, source_group="Study A (950-expansion)"):
    """Add RESERVED rows for candidates not already present under any status. Returns (rows, rejected_dupes)."""
    idx = registry_index(rows)
    dupes = []
    for c in candidates:
        reg = domain_utils.registrable_domain(c)
        if reg in idx:
            dupes.append((c, idx[reg]["status"]))
            continue
        new_row = {
            "canonical_root_domain": c,
            "registrable_domain": reg,
            "source_group": source_group,
            "category": "UNKNOWN",
            "sampling_stratum": "UNKNOWN",
            "status": "RESERVED",
            "batch_id": batch_id,
        }
        rows.append(new_row)
        idx[reg] = new_row
    return rows, dupes


def _transition(rows, domains, batch_id, target_status):
    """
    Shared enforcement for commit_domains/reject_domains: only a domain
    that is currently RESERVED under EXACTLY this batch_id may transition
    to target_status. Everything else raises RegistryStateError -- a
    coordinator bug (wrong batch_id, committing something never reserved,
    or trying to touch an immutable row) must be loud, never silently
    ignored or silently overwritten.
    """
    idx = registry_index(rows)
    for d in domains:
        reg = domain_utils.registrable_domain(d)
        if reg not in idx:
            raise RegistryStateError(
                f"{d}: not present in the registry at all -- a domain must be reserve_domains()'d "
                f"before it can transition to {target_status}."
            )
        row = idx[reg]
        if row["status"] in IMMUTABLE_STATUSES:
            raise RegistryStateError(
                f"{d}: status={row['status']} is immutable and can never transition (attempted -> {target_status})."
            )
        if row["status"] != "RESERVED":
            raise RegistryStateError(
                f"{d}: status={row['status']} -> {target_status} is not a legal transition "
                f"(only RESERVED -> COMMITTED/REJECTED is allowed)."
            )
        if row["batch_id"] != batch_id:
            raise RegistryStateError(
                f"{d}: reserved under batch_id={row['batch_id']!r}, cannot be transitioned to {target_status} "
                f"by a different batch_id={batch_id!r} -- another wave's reservation is off-limits."
            )
        row["status"] = target_status
    return rows


def commit_domains(rows, domains, batch_id):
    """RESERVED (this batch_id only) -> COMMITTED. Raises RegistryStateError on any illegal transition."""
    return _transition(rows, domains, batch_id, "COMMITTED")


def reject_domains(rows, domains, batch_id):
    """RESERVED (this batch_id only) -> REJECTED. Raises RegistryStateError on any illegal transition."""
    return _transition(rows, domains, batch_id, "REJECTED")


def merge_wave_into_master(wave_csv: Path, master_csv: Path):
    """
    Append a validated wave's rows (already Gate-PASSed on their own) into
    the master Study A dataset CSV, checking for column-set match and
    duplicate canonical_root_domain against the existing master rows.
    Does not run the Gate itself -- callers must Gate-validate the wave
    CSV (and ideally the merged master) before/after calling this.
    """
    with open(wave_csv, newline="", encoding="utf-8") as f:
        wave_reader = csv.DictReader(f)
        wave_fieldnames = wave_reader.fieldnames
        wave_rows = list(wave_reader)

    if master_csv.exists():
        with open(master_csv, newline="", encoding="utf-8") as f:
            master_reader = csv.DictReader(f)
            master_fieldnames = master_reader.fieldnames
            master_rows = list(master_reader)
        if wave_fieldnames != master_fieldnames:
            raise ValueError(
                f"Column mismatch: wave file has {wave_fieldnames} but master has {master_fieldnames}"
            )
    else:
        master_fieldnames = wave_fieldnames
        master_rows = []

    existing_domains = {r["canonical_root_domain"] for r in master_rows}
    new_domains = {r["canonical_root_domain"] for r in wave_rows}
    overlap = existing_domains & new_domains
    if overlap:
        raise ValueError(f"Duplicate canonical_root_domain(s) between wave and master: {sorted(overlap)}")

    # Registrable-domain-based check too (Item 4): two different raw strings
    # (e.g. "www.example.com" that slipped through clean-root-form validation
    # elsewhere, or a genuine same-domain-different-casing typo) must not both
    # end up in the master dataset even if their raw canonical_root_domain
    # strings happen to differ.
    existing_reg = {domain_utils.registrable_domain(d) for d in existing_domains}
    new_reg = {domain_utils.registrable_domain(d) for d in new_domains}
    reg_overlap = existing_reg & new_reg
    if reg_overlap:
        raise ValueError(
            f"Duplicate registrable domain(s) between wave and master (raw strings may differ): {sorted(reg_overlap)}"
        )

    merged = master_rows + wave_rows
    with open(master_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=master_fieldnames)
        writer.writeheader()
        for r in merged:
            writer.writerow(r)
    return len(merged)


def main():
    parser = argparse.ArgumentParser(description="Build/update the Domain Registry.")
    parser.add_argument("--a0-csv", default=str(Path(__file__).parent.parent / "validation_50_v2.csv"),
                         help="Study A cumulative CSV to seed as COMMITTED (default: validation_50_v2.csv)")
    parser.add_argument("--pilot-csv", default=None,
                         help="Path to the original 100-site pilot study's sites.csv (pre-V2 schema, "
                              "uses a 'domain' column), to seed as EXCLUDED_PRIOR_PILOT.")
    parser.add_argument("--out", default=str(REGISTRY_PATH))
    args = parser.parse_args()

    rows = []
    rows.extend(seed_committed_from_a0(Path(args.a0_csv)))

    if args.pilot_csv:
        pilot_path = Path(args.pilot_csv)
        if not pilot_path.exists():
            print(f"BLOCKER: --pilot-csv path does not exist: {pilot_path}", file=sys.stderr)
            return 1
        rows.extend(seed_excluded_from_pilot(pilot_path))
    else:
        print(
            "NOTE: --pilot-csv not supplied; EXCLUDED_PRIOR_PILOT rows were NOT seeded. "
            "Re-run with --pilot-csv <path to pilot-100/sites.csv> to seed them.",
            file=sys.stderr,
        )

    # Sanity: no duplicate registrable_domain across the seeded set. This is a
    # hard FAIL (non-zero exit), not a warning (Item 4) -- an overlap between
    # A0/COMMITTED and the prior pilot's EXCLUDED_PRIOR_PILOT would mean a
    # domain that should have been off-limits was researched anyway, which is
    # exactly the kind of silent duplicate the registry exists to prevent.
    seen = {}
    dupes_found = []
    for r in rows:
        reg = r["registrable_domain"]
        if reg in seen:
            dupes_found.append((reg, seen[reg]["canonical_root_domain"], seen[reg]["status"],
                                 r["canonical_root_domain"], r["status"]))
        seen[reg] = r
    if dupes_found:
        print("FAIL: duplicate registrable_domain(s) found across seeded registry data "
              "(a domain should never appear under two different statuses/sources):", file=sys.stderr)
        for reg, dom1, st1, dom2, st2 in dupes_found:
            print(f"  {reg}: {dom1} ({st1}) vs {dom2} ({st2})", file=sys.stderr)
        return 1

    out_path = Path(args.out)
    save_registry(out_path, rows)
    status_counts = {}
    for r in rows:
        status_counts[r["status"]] = status_counts.get(r["status"], 0) + 1
    print(f"Wrote {len(rows)} rows to {out_path}")
    print(f"Status distribution: {status_counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
