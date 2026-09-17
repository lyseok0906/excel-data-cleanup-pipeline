# Validation tooling

Stdlib-only Python (no third-party dependencies, no network access required). Run from anywhere; paths default relative to this script's location.

```bash
# Regenerate validation_10_v2.csv from validation_10.csv
python migrate_schema.py

# Run the Protocol V2 Validation Gate against validation_10_v2.csv
python run_gate_v2.py
# exit code 0 = all checks passed, 1 = at least one FAIL

# Run the regression/self-test suite
python -m unittest test_validation_tooling.py -v
```

- `domain_utils.py` — registrable-domain (eTLD+1) canonicalization, used by `run_gate_v2.py` for duplicate detection. Embeds a curated list of common multi-label public suffixes (co.uk, com.au, etc.) since this environment has no network/dependency access to a full Public Suffix List package (e.g. `tldextract`). See the module docstring for the known limitation and the drop-in replacement path if `tldextract` becomes available later.
- `migrate_schema.py` — reproducible migration from the raw A0-Phase1 schema (`validation_10.csv`) to the Protocol V2 canonical schema (`validation_10_v2.csv`). All provenance-URL backfills and the traffic_scope-aware `traffic_tier` rule are baked into this script (not applied as one-off patches afterward).
- `run_gate_v2.py` — the Protocol V2 Validation Gate (research_protocol_v2.md Section 7). Accepts an optional CSV path argument; defaults to `../validation_10_v2.csv`.
- `test_validation_tooling.py` — regression tests for the fixes made after the GPT independent review of commit `40732be` (see research_protocol_v2.md Section 7-B): domain canonicalization, provenance note-fallback removal, traffic_scope/tier forcing, gate exit codes, and migration reproducibility.
