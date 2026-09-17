# Validation tooling

Stdlib-only Python (no third-party dependencies, no network access required). Run from anywhere; paths default relative to this script's location.

```bash
# Regenerate validation_10_v2.csv from validation_10.csv
python migrate_schema.py

# Build the A0-Phase2 40 new sites (Excel, Personal Finance, Home/DIY & Food,
# Product Review) directly in V2 canonical schema, and concatenate with the
# existing 10 into validation_50_v2.csv
python build_a0_phase2.py

# Run the Protocol V2 Validation Gate against any CSV (defaults to ../validation_10_v2.csv)
python run_gate_v2.py
python run_gate_v2.py ../validation_50_v2.csv --report ../gate_report_50.txt
# exit code 0 = all checks passed, 1 = at least one FAIL

# Run the regression/self-test suite
python -m unittest test_validation_tooling.py -v

# Generate an automated, dataset-neutral summary (row/category/stratum/
# evidence-tier distributions, UNKNOWN rates, field completion, etc.)
python summarize_dataset.py ../validation_50_v2.csv --out ../summary_50.txt

# (Re)build the Domain Registry (research/blog-monetization/registry/domain_registry.csv),
# seeding COMMITTED rows from the current Study A cumulative CSV. Pass
# --pilot-csv <path to blog-monetization-100/sites.csv> to also seed the
# 97 unique prior-pilot domains as EXCLUDED_PRIOR_PILOT (that file is not
# present in every checkout -- see the module docstring for details).
python build_domain_registry.py [--a0-csv ../validation_50_v2.csv] [--pilot-csv ...]
```

- `domain_utils.py` — registrable-domain (eTLD+1) canonicalization, used by `run_gate_v2.py` for duplicate detection. Embeds a curated list of common multi-label public suffixes (co.uk, com.au, etc.) since this environment has no network/dependency access to a full Public Suffix List package (e.g. `tldextract`). See the module docstring for the known limitation and the drop-in replacement path if `tldextract` becomes available later. **Status as of the pre-950 hardening round (2026-09-17): still blocked** -- both a direct network attempt (`Bash`/curl/pip, blocked 403 by org egress policy for `pypi.org` and `raw.githubusercontent.com`) and a `WebFetch`-based attempt (technically reachable, but WebFetch summarizes/paraphrases content via a small model rather than returning it byte-for-byte, which is unsafe for a 10,000+ line correctness-critical data file) were tried and rejected. Do not expand the manual suffix list further; a full PSL swap-in requires either a future environment with real network/pip access, or the user pinning an official PSL snapshot file into the repo from their own machine.
- `evidence_harden.py` — shared post-processing pass (new, pre-950 hardening round) applied to every generated row in both generator scripts below, enforcing: (1) a non-UNKNOWN value must carry a non-UNKNOWN evidence tier (the directional complement of Rule #8); (2) evidence in {A, B, C} must carry a real dedicated `_source_url` (C is auto-backfilled with the site's own homepage URL if missing; A/B raise instead of guessing); (3) evidence == D must carry a non-empty `_note` (auto-filled with a transparent placeholder if missing). Raises `EvidenceHardenError` on any inconsistency it cannot safely resolve, so real defects surface at generation time rather than only at Gate time.
- `migrate_schema.py` — reproducible migration from the raw A0-Phase1 schema (`validation_10.csv`) to the Protocol V2 canonical schema (`validation_10_v2.csv`). All provenance-URL backfills and the traffic_scope-aware `traffic_tier` rule are baked into this script (not applied as one-off patches afterward). Also exposes `FIELDNAMES` and `traffic_tier_for()`, reused by `build_a0_phase2.py`. Runs all rows through `evidence_harden.harden_rows()` before writing.
- `build_a0_phase2.py` — builds the A0-Phase2 40 new-site rows directly in the V2 canonical schema (not a migration -- these are new research entries) and concatenates them with the existing 10 into `validation_50_v2.csv`. All facts/URLs were gathered by dedicated research passes before this script was written; the script only assembles and validates structure (enforces Rule #8, computes `traffic_tier` from `traffic_scope`, checks for column/row-order mismatches and duplicate domains within the batch). Runs all rows through `evidence_harden.harden_rows()` before writing. As of the pre-950 hardening round, `traffic_scope` reflects domain *structure* (content-publisher vs. SaaS/app-mixed vs. subdirectory-estimate), not merely whether a traffic number was found -- see research_protocol_v2.md Section 3-6 -- and `revenue_value` is always either `UNKNOWN` or a single clean structured figure, never descriptive/compound/acquisition text (see Section 7-C item 3).
- `run_gate_v2.py` — the Protocol V2 Validation Gate (research_protocol_v2.md Section 7). Accepts an optional CSV path argument; defaults to `../validation_10_v2.csv`. As of the pre-950 hardening round this runs 13 sections (added: value-requires-evidence directional check, D-tier-requires-note check, `revenue_value` format check) and its final summary line is dataset-neutral (`VALIDATION GATE PASS -- rows=N`) rather than hardcoded to "A0-Phase1".
- `summarize_dataset.py` — automated, dataset-neutral summary generator (new, pre-950 hardening round). Computes row count, category/sampling_stratum/traffic_scope/traffic_tier distributions, `is_contrast_case` counts (kept explicitly separate from `sampling_stratum == "Contrast Cohort"` counts -- these are different axes), per-field UNKNOWN rate and completion rate, and the evidence-tier distribution (with a self-check: `N evidence-bearing fields x N rows` printed alongside the actual count, so an arithmetic mismatch like the earlier hand-written report's "550 vs 500" error is structurally impossible). Replaces all manual/hand-typed aggregation in reports going forward.
- `build_domain_registry.py` — Domain Registry builder/tooling (new, pre-950 hardening round) for the future wave-based 950-site expansion. Maintains `research/blog-monetization/registry/domain_registry.csv` (one row per canonical root domain, `status` in {EXCLUDED_PRIOR_PILOT, RESERVED, COMMITTED, REJECTED}) and exposes `reserve_domains()` / `commit_domains()` / `reject_domains()` / `check_duplicate()` / `merge_wave_into_master()` for a future wave script to call. Currently seeds the 50 A0-cumulative domains as COMMITTED; seeding the prior 100-site pilot's 97 unique domains as EXCLUDED_PRIOR_PILOT is supported via `--pilot-csv` but blocked in this checkout because `research/blog-monetization-100/sites.csv` is not present here -- see the module docstring.
- `test_validation_tooling.py` — regression tests for the fixes made after the GPT independent review of commit `40732be` (see research_protocol_v2.md Section 7-B): domain canonicalization, provenance note-fallback removal, traffic_scope/tier forcing, gate exit codes, and migration reproducibility. Re-run and confirmed 12/12 PASS, unmodified, after the pre-950 hardening round's changes (Section 7-C).
