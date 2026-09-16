import csv, re
from collections import Counter

path = "/home/claude/research/blog-monetization-100/v2_validation/validation_10_v2.csv"
with open(path, newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

report = []
def log(s=""):
    report.append(s); print(s)

VALID_BOOL = {'Y','N','UNKNOWN'}
VALID_EV = {'A','B','C','D','UNKNOWN'}
VALID_TRAFFIC_SCOPE = {'CONTENT_ONLY','WHOLE_DOMAIN_INCLUDES_PRODUCT','SUBDIRECTORY_ESTIMATE','UNKNOWN'}
VALID_CONTRAST_PATTERN = {'shutdown','traffic_decline','cadence_drop','low_traction_despite_age','historically_declined','NOT_APPLICABLE'}
BOOL_FIELDS = ['is_niche_authority','is_contrast_case','display_ads','affiliate','own_product','course_or_community','newsletter_email_capture']
ISO_DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')

log(f"=== Row count: {len(rows)} ===\n")

# 1. Enum validation
log("--- 1. Enum validation ---")
violations = []
for i, r in enumerate(rows):
    for f in BOOL_FIELDS:
        v = r[f].strip()
        if v not in VALID_BOOL:
            violations.append((r['canonical_root_domain'], f, v))
        ev = r[f+'_evidence'].strip()
        if ev not in VALID_EV:
            violations.append((r['canonical_root_domain'], f+'_evidence', ev))
    if r['traffic_scope'].strip() not in VALID_TRAFFIC_SCOPE:
        violations.append((r['canonical_root_domain'], 'traffic_scope', r['traffic_scope']))
    if r['contrast_pattern'].strip() not in VALID_CONTRAST_PATTERN:
        violations.append((r['canonical_root_domain'], 'contrast_pattern', r['contrast_pattern']))
    for f in ['traffic_evidence','revenue_evidence','start_year_evidence']:
        ev = r[f].strip()
        if ev not in VALID_EV:
            violations.append((r['canonical_root_domain'], f, ev))
if violations:
    log(f"FAIL: {len(violations)} violations:")
    for v in violations: log(f"  {v}")
else:
    log("PASS: all boolean/evidence/enum fields (incl. traffic_scope, contrast_pattern) use only allowed values.")
log()

# 2. Mixed value+evidence check
log("--- 2. Mixed value+evidence in single cell check ---")
mixed = []
pat = re.compile(r'\([A-D]\)')
for r in rows:
    for f in BOOL_FIELDS + ['start_year_value','traffic_value_raw','revenue_value']:
        v = r.get(f,'')
        if pat.search(v):
            mixed.append((r['canonical_root_domain'], f, v))
log("PASS: no mixed value+evidence strings found." if not mixed else f"FAIL: {mixed}")
log()

# 3. Duplicate domain check
log("--- 3. Duplicate canonical_root_domain check ---")
domains = [r['canonical_root_domain'].strip().lower() for r in rows]
dupes = [d for d,c in Counter(domains).items() if c>1]
log(f"PASS: all {len(domains)} domains unique." if not dupes else f"FAIL: dupes {dupes}")
log()

# 4. Provenance/source validation -- EVERY evidence-bearing field (not just traffic/revenue) needs a source when A/B
log("--- 4. Provenance / source_url validation (all evidence-bearing fields) ---")
missing_source = []
for r in rows:
    for f in BOOL_FIELDS:
        ev = r[f+'_evidence'].strip()
        url = r.get(f+'_source_url','').strip()
        note = r.get(f+'_note','').strip()
        if ev in ('A','B'):
            has = url.startswith('http') or 'http' in note
            if not has:
                missing_source.append((r['canonical_root_domain'], f, ev, url))
    for base_f, urlfield in [('traffic','traffic_source_url'), ('revenue','revenue_source_url'), ('start_year','start_year_source_url')]:
        ev = r[base_f+'_evidence'].strip()
        url = r.get(urlfield,'').strip()
        note = r.get(base_f+'_note','').strip()
        if ev in ('A','B'):
            has = url.startswith('http') or 'http' in note
            if not has:
                missing_source.append((r['canonical_root_domain'], base_f, ev, url))
if missing_source:
    log(f"FAIL: {len(missing_source)} A/B-evidence fields missing a source URL (in dedicated column or note):")
    for m in missing_source: log(f"  {m}")
else:
    log("PASS: every field carrying A or B evidence has a source URL present (dedicated _source_url column or explicit URL in _note).")
log()

# 5. Date-format validation (ISO on research_date fields; period fields are free text and exempt)
log("--- 5. Date-format validation ---")
date_fields = ['traffic_research_date','revenue_research_date']
bad_dates = []
for r in rows:
    for f in date_fields:
        v = r[f].strip()
        if v != 'UNKNOWN' and not ISO_DATE_RE.match(v):
            bad_dates.append((r['canonical_root_domain'], f, v))
if bad_dates:
    log(f"FAIL: {len(bad_dates)} non-ISO or malformed date cells:")
    for b in bad_dates: log(f"  {b}")
else:
    log("PASS: all traffic_research_date / revenue_research_date cells are clean ISO (YYYY-MM-DD) or explicit UNKNOWN -- no descriptive text baked into date fields.")
# confirm period/description fields are NOT required to be ISO (they are separate, free-text by design)
log("Note: traffic_source_period / revenue_figure_period / traffic_value_raw_period are free-text PERIOD descriptors by design, kept separate from the ISO research_date fields above -- this is the fix for the prior 'descriptive text in date field' problem.")
log()

# 6. UNKNOWN value -> UNKNOWN evidence rule (Rule #8)
log("--- 6. UNKNOWN value implies UNKNOWN evidence (Rule #8) ---")
rule8_violations = []
check_pairs = [(f, f+'_evidence') for f in BOOL_FIELDS] + [('traffic_value_raw','traffic_evidence'), ('revenue_value','revenue_evidence'), ('start_year_value','start_year_evidence')]
for r in rows:
    for vf, ef in check_pairs:
        v = r[vf].strip()
        ev = r[ef].strip()
        if v == 'UNKNOWN' and ev != 'UNKNOWN':
            rule8_violations.append((r['canonical_root_domain'], vf, v, ef, ev))
if rule8_violations:
    log(f"FAIL: {len(rule8_violations)} rows violate Rule #8 (UNKNOWN value with non-UNKNOWN evidence):")
    for v in rule8_violations: log(f"  {v}")
else:
    log("PASS: every UNKNOWN-valued field carries UNKNOWN evidence (2 pre-existing violations from validation_10.csv -- fortelabs.com/affiliate and asianefficiency.com/affiliate -- were corrected during migration).")
log()

# 7. traffic_scope / traffic_tier consistency check (Section 4-1 rule)
log("--- 7. traffic_scope / traffic_tier consistency check (Section 4-1 rule) ---")
scopes = Counter(r['traffic_scope'] for r in rows)
log(f"traffic_scope distribution: {dict(scopes)}")
scope_tier_violations = []
for r in rows:
    scope = r['traffic_scope'].strip()
    tier = r['traffic_tier'].strip()
    if scope == 'WHOLE_DOMAIN_INCLUDES_PRODUCT' and tier != 'UNKNOWN':
        scope_tier_violations.append((r['canonical_root_domain'], scope, tier, 'expected UNKNOWN per Section 4-1'))
    if scope == 'UNKNOWN' and tier != 'UNKNOWN':
        scope_tier_violations.append((r['canonical_root_domain'], scope, tier, 'expected UNKNOWN per Section 4-1'))
    # raw value must still be preserved (not blanked out) even when tier is forced UNKNOWN
    if scope == 'WHOLE_DOMAIN_INCLUDES_PRODUCT' and r['traffic_value_raw'].strip() in ('', 'UNKNOWN'):
        scope_tier_violations.append((r['canonical_root_domain'], scope, r['traffic_value_raw'], 'raw value should be preserved, not blanked, for WHOLE_DOMAIN_INCLUDES_PRODUCT'))
if scope_tier_violations:
    log(f"FAIL: {len(scope_tier_violations)} traffic_scope/traffic_tier rule violations:")
    for v in scope_tier_violations: log(f"  {v}")
else:
    log("PASS: traffic_tier correctly forced to UNKNOWN wherever traffic_scope is WHOLE_DOMAIN_INCLUDES_PRODUCT or UNKNOWN, and raw traffic values remain preserved (not deleted).")
whole_domain = [r['canonical_root_domain'] for r in rows if r['traffic_scope']=='WHOLE_DOMAIN_INCLUDES_PRODUCT']
log(f"Sites flagged as whole-domain (excluded from content-level traffic_tier comparisons, raw value retained): {whole_domain}")
log()

# 8. contrast_pattern structure check
log("--- 8. contrast_pattern structure check ---")
for r in rows:
    if r['is_contrast_case'] == 'Y':
        log(f"  {r['canonical_root_domain']}: contrast_pattern={r['contrast_pattern']}, evidence_period='{r['contrast_evidence_period'][:80]}...'")
log()

# 9. sampling_stratum vs traffic_tier vs is_niche_authority independence check
log("--- 9. Dimension-independence check (sampling_stratum vs traffic_tier vs is_niche_authority) ---")
for r in rows:
    log(f"  {r['canonical_root_domain']}: stratum={r['sampling_stratum']} | traffic_tier={r['traffic_tier']} | is_niche_authority={r['is_niche_authority']} | is_contrast_case={r['is_contrast_case']}")
mismatch = [r['canonical_root_domain'] for r in rows if r['sampling_stratum']=='Large/Traffic Leader' and r['traffic_tier']=='LOW']
log(f"Example of dimension mismatch surfaced (stratum=Large/Traffic Leader but traffic_tier=LOW): {mismatch}")
log()

# 10. Denominator automation test
log("--- 10. Denominator automation test ---")
for f in ['affiliate','display_ads','own_product','is_niche_authority','is_contrast_case']:
    vals = [r[f].strip() for r in rows]
    denom = sum(1 for v in vals if v in ('Y','N'))
    num = sum(1 for v in vals if v == 'Y')
    log(f"  {f}: {num} of {denom} confirmed = Y (direct column filter, no parsing)")
log("PASS: denominators computable via direct column filter across all migrated fields.")
log()

with open("/home/claude/research/blog-monetization-100/v2_validation/gate_report_v2.txt","w") as f:
    f.write("\n".join(report))
print("\nWrote gate_report_v2.txt")
