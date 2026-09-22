# QA / Publish-Readiness Package — "excel-trim-not-removing-nonbreaking-space"

Source article: `content/excel-trim-not-removing-nonbreaking-space.md`
Predecessor: Pilot C (`TRIM vs CHAR(160)`, Simple Task grade, but actual human-intervention cost was much higher than typical Simple Task — see decision log "생산성 / 사람 개입 정도" table) — no `content/pilot_C_*.md` file exists in this repo; the only prior record is `claude/비즈니스_방향_결정_로그.md` (2026-09-15 "Pilot C/D/E 실측 결과 및 Gate 판단" section) and `docs/pilot_results.md`'s summary row.
Prepared: 2026-09-22
Prepared by: Cowork (assistant), per `docs/content_operations_playbook.md`, using **only facts already recorded in the decision log — no new research, no new Excel reproduction this round** (per standing user instruction for Pilot A–E conversions). Official Microsoft doc URLs were looked up this round for citation purposes only (source-citation verification, consistent with how Pilot A/B handled this — not new investigation into behavior).

---

## 1. Article Metadata (for WordPress, NOT uploaded)

| Field | Value |
|---|---|
| Title | Why TRIM Isn't Removing All Spaces in Excel (Non-Breaking Space Fix) |
| Slug | `excel-trim-not-removing-nonbreaking-space` |
| Meta description | TRIM in Excel only removes regular spaces, not non-breaking spaces (U+00A0). Here's how to detect and remove them — and a locale bug to watch for. (155 chars) |
| Category | Text Cleanup |
| Search Intent | Troubleshooting / Fix |
| QA grade (per `docs/qa_policy.md`) | Simple Task — **note:** decision log records that Pilot C's actual verification cost (6 screenshot round-trips, multiple diagnostic formulas to isolate the locale bug) was much higher than typical for this grade; this is flagged as a known exception, not a reason to reclassify the grade itself |
| Focus keyword (Rank Math) | excel trim not removing space |
| Version scope | All current Excel versions (formula-based, not a version-gated feature). The `CHAR(160)` locale bug is a Windows-locale/codepage issue confirmed on Korean-language Windows, not an Excel-version issue |
| Internal link candidates | `excel-remove-blank-rows-guide` (Pilot G, production draft exists, not yet published); `power-query-remove-duplicates` (Pilot A, production draft exists, not yet published) — **neither linked in-body**, since neither is a live published URL yet |

## 2. Claim-by-Claim Evidence Map (no new research or reproduction performed this round)

| # | Claim in article | Evidence source | Status |
|---|---|---|---|
| 1 | `TRIM` removes leading/trailing regular spaces and collapses multiple regular spaces between words, but does not remove non-breaking space (code 160) | [TRIM function](https://support.microsoft.com/en-us/excel/functions/trim-function) — Microsoft Support, states this explicitly (per the wording already confirmed and quoted in the decision log's Pilot F ChatGPT-review-revision entry) | **Official doc, directly on point** — this is the strongest possible source, stronger than a project reproduction alone |
| 2 | `CLEAN` removes ASCII control characters (codes 0–31) and does not affect code 160 | [CLEAN function](https://support.microsoft.com/en-us/excel/functions/clean-function) — Microsoft Support | Official doc |
| 3 | `UNICHAR(n)` returns the character for Unicode code point `n`, independent of ANSI codepage | [UNICHAR function](https://support.microsoft.com/en-us/excel/functions/unichar-function) — Microsoft Support | Official doc |
| 4 | On the reproduced system (Excel 2021, Korean-language Windows), `CHAR(160)` returns a regular space (code 32) instead of the true non-breaking space, while `UNICHAR(160)` correctly returns code 160 | Decision log, Pilot C `[Observed]` — diagnosed via `UNICODE(MID(...))` character inspection and `=UNICODE(CHAR(160))` / `=UNICODE(UNICHAR(160))` direct tests | **Project-verified reproduction** — root cause independently diagnosed, not inferred |
| 5 | The `CHAR(160)`-based fix formula fails silently (no error, just doesn't fix the text) rather than erroring out | Same decision log entry — the SUBSTITUTE had "nothing matching to replace" because CHAR(160) wasn't returning code 160 | Project-verified reproduction |
| 6 | This is a locale/codepage-dependent issue that could affect other non-Western Windows locales, not confirmed exhaustively | Decision log explicitly frames this as an ANSI-codepage dependency, but the reproduction was done on one specific locale (Korean-language Windows) only | **Scope-limited claim, not overgeneralized** — matches the ChatGPT-review correction already applied to Pilot F's NBSP section (avoid "all non-Western locales" language) |

**Conclusion:** every claim in the article traces either to an official Microsoft doc (claims 1–3) or to this project's own diagnosed reproduction of the locale bug (claims 4–5), with claim 6 explicitly scoped to avoid overgeneralizing beyond what was actually tested — the same correction ChatGPT's review already required for Pilot F's NBSP section, applied proactively here.

## 3. Technical QA Checklist

| # | Item | Result |
|---|---|---|
| 1 | Every formula in the article is syntactically valid and matches documented function behavior | PASS |
| 2 | Every claimed behavior matches either official Microsoft documentation or project-recorded verification | PASS — this article is unusually well-grounded: its single most important claim (TRIM doesn't remove NBSP) is directly stated in Microsoft's own TRIM doc, not just inferred |
| 3 | Retained reproduction evidence (fixture and/or screenshot) exists | **FAIL / NOT YET MET** — no fixture file for this topic exists in this repo (the original Pilot C/D/E lightweight fixture, `blog_b_pilot_cde_fixture_lite.xlsx`, was never migrated to `fixtures/`), and no screenshots exist. Same primary blocker pattern as Pilot A/B. |
| 4 | Version applicability statement is accurate | PASS — correctly framed as a locale/codepage issue rather than a version issue, and explicitly not overgeneralized past what was tested (Korean-language Windows only) |
| 5 | No known Blog B content trap is present, and this article's own trap (the `CHAR(160)` vs `UNICHAR(160)` locale bug) is stated correctly per the standing content-accuracy requirement in the decision log | PASS — this article **is** the canonical source of that trap; verified against the decision log's exact wording of the required fix |

## 4. Fixture and Screenshot Requirements (NOT YET CAPTURED — primary blocker)

No fixture exists in this repo for this topic under `fixtures/`. Planned fixture (for a future round): one workbook with at least two cases — (a) a cell with a true non-breaking space (U+00A0) padding the text, and (b) a cell with a non-breaking space between two words — plus a column showing the `CHAR(160)` vs `UNICHAR(160)` codepage difference directly (e.g., `=UNICODE(CHAR(160))` and `=UNICODE(UNICHAR(160))` as visible formulas), captured on the same locale where the original bug was found if possible, since the bug is locale-dependent and may not reproduce on an English-language Windows machine.

| # | Scenario | Screenshot content needed | Alt text (draft) |
|---|---|---|---|
| 1 | NBSP padding a cell, TRIM alone fails | Formula bar with `=TRIM(A2)`, result still showing extra space / LEN mismatch | "TRIM formula failing to remove a non-breaking space in Excel" |
| 2 | Character-code diagnosis | `=UNICODE(MID(A2,1,1))` returning 160 | "UNICODE formula confirming a non-breaking space at code 160" |
| 3 | The locale bug itself | `=UNICODE(CHAR(160))` returning 32 instead of 160 (on the affected locale) | "CHAR(160) returning the wrong character code on a non-Western Windows locale" |
| 4 | The working fix | `=UNICODE(UNICHAR(160))` returning 160, and the full fix formula producing the correct trimmed result | "UNICHAR(160) correctly returning the non-breaking space regardless of locale" |
| 5 | Before/after full fix formula | `=TRIM(SUBSTITUTE(CLEAN(A2),UNICHAR(160)," "))` result matching expected clean text and LEN | "Full fix formula removing non-breaking spaces and matching expected text length" |

**Status: blocking**, same as Pilot A/B. English-UI capture required from the start. Given the bug is locale-dependent, screenshot 3 specifically may need to be captured on the same non-English Windows locale where it was originally found, or clearly caveated if captured on an English-locale machine where `CHAR(160)` may behave correctly.

## 5. SEO/Search-Intent QA Checklist

| # | Item | Result |
|---|---|---|
| 1 | Focus keyword appears naturally in title, meta description, and body | PASS |
| 2 | Title matches search intent (Troubleshooting/Fix) and states the concrete symptom | PASS |
| 3 | Meta description is under ~160 characters | PASS (155 chars) |
| 4 | Headings (H2s) map onto distinct, scannable sub-tasks (why it fails, the fix, the locale bug, how to verify) | PASS |
| 5 | No keyword-density padding | PASS |
| 6 | Internal links only point to pages that actually exist | PASS — none inserted this round |

## 6. US English QA Checklist

| # | Item | Result |
|---|---|---|
| 1 | US spelling/vocabulary conventions throughout | PASS |
| 2 | Instructions use standard Excel formula/menu terminology | PASS |
| 3 | Grammar, punctuation, and formula/code-block formatting are correct and consistent | PASS |
| 4 | Tone matches Blog B's plain, task-focused style | PASS |
| 5 | Scope of the locale claim is worded carefully (avoids "all non-Western locales" overgeneralization) | PASS — matches the correction ChatGPT's review already applied to Pilot F's NBSP section |

## 7. Publish-Readiness Status

- WordPress upload: **NOT performed** — Draft-only, per instruction (public publish requires separate user approval).
- Repo storage: article and this QA package to be committed to the repo this round; `docs/content_status.md` updated in the same commit.
- Fixture: **does not exist yet** — primary blocker (§4).
- Screenshot evidence: **does not exist yet** — primary blocker (§4), depends on the fixture above, and may need locale-specific capture.
- Residual risk: the locale bug has been confirmed on exactly one Windows locale (Korean-language Windows); the article's wording is scoped to avoid claiming it affects "all" non-Western locales, but this should be kept in mind if screenshot capture happens on a different locale and the bug doesn't reproduce there.
- Human Approval: not requested this round.

## 8. Final Verdict

**DRAFT — TECHNICALLY SOUND, STRONGLY EVIDENCED, NOT YET SCREENSHOT-COMPLETE.**

Rationale: this article's central technical claim (TRIM doesn't remove non-breaking spaces) is stated directly in Microsoft's own official TRIM documentation — stronger grounding than most Pilot A/B claims, which often relied on inference from documented mechanics. The locale bug (`CHAR(160)` vs `UNICHAR(160)`) is a project-verified, root-cause-diagnosed reproduction, not a guess. No new research or Excel reproduction was performed this round. The article is **not** yet CONTENT READY solely because, like Pilot A/B/G, no fixture or screenshots exist yet (§4) — this is a Simple Task grade per `docs/qa_policy.md`, so the bar for evidence is lower than Pilot A/B's High-risk Integrated Guide grade, but Technical QA item 3 is still marked FAIL until at least the "how to check whether this affects you" formulas are shown working in a real screenshot. Next in sequence: Pilot D.
