# QA / Publish-Readiness Package — "excel-split-comma-values-into-rows"

Source article: `content/excel-split-comma-values-into-rows.md`
Predecessor: Pilot B (`excel split comma separated values into rows`, LIVE TEST T1) — no `content/pilot_B_*.md` file exists in this repo; the only prior record is `claude/비즈니스_방향_결정_로그.md` (2026-09-10 LIVE TEST spec, 2026-09-15 independent verification entries) and `docs/pilot_results.md`'s summary row.
Prepared: 2026-09-22
Prepared by: Cowork (assistant), per `docs/content_operations_playbook.md`, using **only facts already recorded in the decision log — no new research, no new Excel reproduction this round**.
Status at end of this package: see "Final Verdict" at the bottom.

---

## 1. Article Metadata (for WordPress, NOT uploaded)

| Field | Value |
|---|---|
| Title | Split Comma-Separated Values into Rows in Excel (TEXTSPLIT vs Power Query) |
| Slug | `excel-split-comma-values-into-rows` |
| Meta description | Split comma-separated values into their own rows in Excel. TEXTSPLIT works in Microsoft 365 and Excel 2024; older versions need the Power Query fallback. (157 chars) |
| Category | Power Query |
| Search Intent | Comparison / Method choice |
| QA grade (per `docs/qa_policy.md`) | High-risk Integrated Guide |
| Focus keyword (Rank Math) | excel split comma separated values into rows |
| Version scope | Microsoft 365, Excel 2024 → `TEXTSPLIT` (native). Excel 2021, 2019, 2016 → Power Query fallback (no `TEXTSPLIT`) |
| Internal link candidates | `power-query-remove-duplicates` (Pilot A, exists as production draft, not yet published); `excel-remove-blank-rows-guide` (Pilot G, same status) — **neither linked in-body**, since neither is a live published URL yet |

## 2. Claim-by-Claim Evidence Map (no new research performed this round)

| # | Claim in article | Evidence source | Status |
|---|---|---|---|
| 1 | `TEXTSPLIT(text, col_delimiter, row_delimiter)` splits into rows via the `row_delimiter` argument | [TEXTSPLIT function](https://support.microsoft.com/en-us/excel/functions/textsplit-function) — Microsoft Support | Official doc, verified this round (URL check only) |
| 2 | `ignore_empty` argument skips blank entries from consecutive delimiters | Same official page | Official doc |
| 3 | `row_delimiter` accepts an array for multiple delimiter characters | Same official page | Official doc |
| 4 | `TEXTSPLIT` is scoped to Microsoft 365 and Excel 2024 | Same official page | Official doc |
| 5 | `TEXTSPLIT` returns `#NAME?` in Excel 2021 (all delimiter/blank/multiple-delimiter cases tested) | Decision log, "LIVE TEST 실행 결과 독립 검증" (2026-09-15) — T1 result, reproduced in the user's actual Excel 2021 | **Project-verified reproduction**, not merely inferred from version-scoping |
| 6 | Power Query "Split Column by Delimiter" with "Rows" option performs the same split on older versions | [Split a column of text (Power Query)](https://support.microsoft.com/en-us/office/split-a-column-of-text-power-query-5282d425-6dd0-46ca-95bf-8e0da9539662) — Microsoft Support | Official doc |
| 7 | Power Query's split-into-rows step has no single built-in "ignore empty" toggle (a separate filter step is needed) | **Project-reproduced 2026-09-30**: fixture row `Apple,,Cherry` split by comma into rows produces a literal blank row; no built-in skip-blank option exists in the Split Column by Delimiter dialog. See `evidence/excel-split-comma-values-into-rows/case6_result_with_blank_row.png` and `case7_filtered_no_blanks.png`. | **RESOLVED — now a project-verified reproduction, not an inference (see Finding F below)** |

**Finding F (RESOLVED 2026-09-30):** claim #7 was previously an unverified inference; it is now a direct project reproduction. Using the fixture's ID 2 row (`Apple,,Cherry`), Split Column by Delimiter (Comma, Rows) produced rows `Apple` / `` (blank) / `Cherry` — confirming there is no built-in "skip blank" toggle and a separate filter step (Home > Remove Rows > Remove Blank Rows, or unchecking `(blank)` in the column filter) is required to remove it. Separately, the fixture's ID 3 row (`Apple;Banana,Cherry`, mixed comma/semicolon) confirmed that splitting by comma only leaves the semicolon-joined portion (`Apple;Banana`) intact in one row — Power Query's Split Column by Delimiter takes exactly one delimiter per step, with no array-of-delimiters equivalent to `TEXTSPLIT`'s `row_delimiter` array. Both findings are now reflected in the article (Method 2, the comparison table, the one-line summary, and the Sources footnote).

**Conclusion:** 6 of 7 claims trace directly to either an official Microsoft page or a project-reproduced result already in the decision log. One claim (#7) is disclosed as unverified inference rather than presented as confirmed fact — consistent with the "no overstated/unconfirmed claims" rule.

## 3. Technical QA Checklist

| # | Item | Result |
|---|---|---|
| 1 | Every formula/UI-step sequence in the article is accurate to current Excel/Power Query behavior as documented | PASS (see claim map above; item 7 flagged, not failed — it's disclosed rather than overstated) |
| 2 | Every claimed behavior matches either official Microsoft documentation or project-recorded verification | PASS — Finding F now resolved by direct reproduction |
| 3 | Retained reproduction evidence (fixture and/or screenshot) exists for each method | **PASS** — `fixtures/excel-split-comma-values-into-rows_fixture.xlsx` built and committed; 7/7 required screenshots captured, verified, and saved to `evidence/excel-split-comma-values-into-rows/` (2026-09-30). |
| 4 | Version applicability statement is accurate | PASS — matches the decision log's LIVE TEST T1/T4 version split exactly |
| 5 | No known Blog B content trap is present (CHAR vs UNICHAR, Text.Combine null-vs-empty-string, Go To Special blank-row deletion) | PASS — none of the three known traps apply to this topic |

## 4. Fixture and Screenshot Requirements (NOT YET CAPTURED — primary blocker)

No fixture exists in this repo for this topic. Planned fixture (for a future round): one workbook with a raw data sheet (comma-separated values in single cells, including at least one cell with consecutive commas and one with a mixed delimiter) and:

| # | Scenario | Screenshot content needed | Alt text (draft) |
|---|---|---|---|
| 1 | TEXTSPLIT basic row split | Formula bar showing `=TEXTSPLIT(A2,,",")`, spilled results in rows below | "TEXTSPLIT formula splitting comma-separated values into rows in Excel" |
| 2 | TEXTSPLIT with `ignore_empty` | Side-by-side: `ignore_empty` FALSE (blank row present) vs TRUE (blank row skipped) | "TEXTSPLIT ignore_empty argument skipping blank entries from consecutive commas" |
| 3 | TEXTSPLIT with multiple delimiters | Formula using a delimiter array, correctly splitting mixed comma/semicolon text | "TEXTSPLIT splitting on multiple delimiters using a delimiter array" |
| 4 | TEXTSPLIT `#NAME?` in Excel 2021 | Same formula entered in Excel 2021 showing `#NAME?` | "TEXTSPLIT formula returning #NAME? error in Excel 2021, which does not support the function" |
| 5 | Power Query Split Column by Delimiter dialog | Dialog with "Rows" selected under "Split into" | "Power Query Split Column by Delimiter dialog with Rows selected" |
| 6 | Power Query result | Resulting table with one row per split value | "Power Query result showing comma-separated values split into individual rows" |
| 7 | Power Query blank-row handling | Before/after of filtering out blank rows produced by consecutive delimiters | "Power Query filter step removing blank rows created by consecutive delimiters" |

**Status: RESOLVED (2026-09-30).** Fixture built (`fixtures/excel-split-comma-values-into-rows_fixture.xlsx`); all 7 screenshots captured in English UI (Excel Online for Cases 1-3, local Excel 2021 for Case 4, local Excel 2021 Power Query for Cases 5-7) and saved to `evidence/excel-split-comma-values-into-rows/`. Case 1-3 screenshot covers all three TEXTSPLIT cases in one image (same worksheet view); Cases 6/7 use before/after screenshots of the same filter step.

## 5. SEO/Search-Intent QA Checklist

| # | Item | Result |
|---|---|---|
| 1 | Focus keyword appears naturally in title, meta description, and body | PASS |
| 2 | Title matches search intent (Comparison/Method choice) and names both methods | PASS |
| 3 | Meta description is under ~160 characters | PASS (157 chars) |
| 4 | Headings (H2s) map onto distinct, scannable sub-tasks | PASS — one H2 per method, plus a comparison table and a troubleshooting section |
| 5 | No keyword-density padding | PASS |
| 6 | Internal links only point to pages that actually exist | PASS — none inserted this round |

## 6. US English QA Checklist

| # | Item | Result |
|---|---|---|
| 1 | US spelling/vocabulary conventions throughout | PASS |
| 2 | Instructions use US Excel/Power Query menu path names | PASS |
| 3 | Grammar, punctuation, and formula/code-block formatting are correct and consistent | PASS |
| 4 | Tone matches Blog B's plain, task-focused style | PASS |

## 7. Publish-Readiness Status

- WordPress upload: **NOT performed** — Draft-only, per instruction (public publish requires separate user approval).
- Repo storage: article, this QA package, fixture, and evidence screenshots committed to the repo; `docs/content_status.md` updated in the same round.
- Fixture: **exists** — `fixtures/excel-split-comma-values-into-rows_fixture.xlsx` (built 2026-09-30).
- Screenshot evidence: **complete** — 7/7 screenshots captured and verified, saved to `evidence/excel-split-comma-values-into-rows/`.
- Residual risk: none outstanding from §2's claim map — Finding F (claim #7) is now resolved by direct reproduction rather than flagged as an inference.
- Human Approval: not requested this round; WordPress Draft creation is the next step.

## 8. Final Verdict

**CONTENT READY — fixture and 7/7 English-UI screenshots captured and verified (2026-09-30). Ready for WordPress Draft creation.**

Rationale: the article's remaining technical claims trace directly to an official Microsoft page or an already-verified project reproduction (the Excel 2021 `#NAME?` finding). The two Power Query claims that were not backed by either (blank-row handling and multiple-delimiter support) are now stated as explicitly unverified rather than presented as fact — see §9. No new research or Excel reproduction was performed this round. Confirmed by independent ChatGPT QA (2026-09-23): the TEXTSPLIT content held up and the softened Power Query language was accepted as-is, no further changes required. Same as Pilot A, this article is **not** yet CONTENT READY only because its High-risk Integrated Guide grade requires fixture-backed screenshots, and none exist yet (§4).

## 9. Revision Round — ChatGPT Independent QA (2026-09-23)

**Verdict received:** 수정 필요 (revision required).

**Issues raised:**
1. The article stated as fact that Power Query's Split Column by Delimiter dialog supports "Custom" with multiple delimiters entered together, or running the split step twice for mixed delimiter types — this claim was never in the QA claim map (§2) and had not been verified by this project, unlike `TEXTSPLIT`'s documented delimiter-array argument.
2. The article stated as fact that Power Query's split-into-rows step has no single toggle for skipping blank results and that a filter step afterward is required — already flagged in §2 as Finding F (an inference, not a verified result), but the article's own wording was more confident than the disclosure in this QA package warranted.

**Changes made:**
1. Removed the "use Custom and enter each delimiter, or run the split step twice" claim from Method 2, and replaced it with an explicit statement that the dialog takes one delimiter per step and that mixed-delimiter behavior "has not been tested" by this project.
2. Rewrote the blank-row-handling paragraph in Method 2 to state plainly that this project has not independently reproduced Power Query's behavior on consecutive delimiters or confirmed whether a built-in skip option exists, rather than asserting "does not have a single toggle" as a confirmed mechanism.
3. Updated the comparison table's "Skips blank splits" and "Multiple delimiters" rows for Power Query to say "not independently verified" instead of describing a specific mechanism.
4. Updated the one-line summary and the Sources footnote to match — both now state plainly that Power Query's blank-row and multi-delimiter behavior for this step has not been verified by this project.

**Not changed:** the TEXTSPLIT-side claims (row_delimiter, ignore_empty, delimiter array, Microsoft 365/2024 scoping, and the Excel 2021 `#NAME?` reproduction) — these are backed by the official Microsoft page or a project-verified reproduction and were not disputed by the QA.

## 10. Fixture / Screenshot Round (2026-09-30)

**Fixture:** `fixtures/excel-split-comma-values-into-rows_fixture.xlsx` — built with openpyxl. `Data` sheet has a `RawData` table (ID/Tags) covering a basic comma list, consecutive commas, mixed comma/semicolon delimiters, no delimiter, and a trailing comma. `TEXTSPLIT_Demo` sheet has 4 live formulas for Cases 1-3 (Microsoft 365/2024 only); `Instructions` sheet is plain text only (no leading `=` on any cell, per the lesson from Pilot A's fixture-corruption incident).

**Issue found and fixed:** the first build of `TEXTSPLIT_Demo`'s formulas returned `#NAME?` even in Excel Online (which does support `TEXTSPLIT`). Root cause: openpyxl writes newer dynamic-array functions without the internal `_xlfn.` prefix Excel needs to resolve the function name, so Excel couldn't recognize `TEXTSPLIT` at all and displayed the formula with a spurious `@` (implicit intersection) prepended. Fixed by writing the formulas as `=_xlfn.TEXTSPLIT(...)`. After the fix, the formulas still showed `@`-prefixed single-value results instead of spilling (a separate openpyxl limitation — it doesn't write the dynamic-array cell metadata Excel needs to spill automatically); resolved by having the user re-enter each formula cell once (F2, Enter) in Excel Online, which cleared the `@` and enabled proper spilling. **Lesson for future fixtures with newer Excel functions (TEXTSPLIT, XLOOKUP, FILTER, SORT, UNIQUE, SEQUENCE, etc.): write them as `=_xlfn.<FUNCTION>(...)` and expect to re-enter each formula cell once after opening in real Excel to clear the `@` and enable spilling.**

**Screenshots (7/7, English UI):**
- Case 1-3 (`case1-3_textsplit_spill_results.png`): captured in Excel Online (TEXTSPLIT requires Microsoft 365/2024 — the user's local Excel is a perpetual Excel 2021 license, so Excel Online was used via the user's OneDrive/Microsoft account, with the browser display language switched to English via Chrome's language settings). Shows all 3 cases spilling correctly in one view.
- Case 4 (`case4_name_error_excel2021.png`): captured in local Excel 2021, confirming `#NAME?` on all 4 TEXTSPLIT formula cells automatically (no separate fixture needed for this case).
- Case 5 (`case5_split_column_dialog.png`): Power Query Split Column by Delimiter dialog, Comma + Rows, captured in local Excel 2021.
- Case 6 (`case6_result_with_blank_row.png`): split result, showing a real blank row for ID 2 (`Apple,,Cherry`) and `Apple;Banana` staying joined for ID 3 (`Apple;Banana,Cherry`) — this directly resolves Finding F (see §2).
- Case 7 (`case7_filtered_no_blanks.png`): same result after filtering blank Tags rows out via the column filter.

**Finding F: RESOLVED.** See §2 for the updated claim-by-claim entry. The article, comparison table, one-line summary, and Sources footnote were all updated to state the Power Query blank-row and multi-delimiter behavior as project-confirmed findings rather than disclosed-as-unverified inferences.

**Next step:** WordPress Draft creation, images/alt text/SEO, then user-initiated publish — same pattern as Pilot A.

## 11. WordPress Draft Created (2026-09-30)

Draft created via REST API (existing logged-in browser session's nonce, no password entry) — post ID **69**, category "Power Query" (existing, id 6), slug `excel-split-comma-values-into-rows`, status `draft`. Content converted to Gutenberg blocks from the final article (post-Finding-F-resolution version), with 5 image placeholder paragraphs marking where the 7 screenshots go (Case 1-3 combined into placeholder 1, Case 4 → placeholder 2, Case 5 → placeholder 3, Case 6 → placeholder 4, Case 7 → placeholder 5). Images to be attached by the user directly in the editor, per the established Pilot A/C/E/G pattern.

**Next step:** user attaches the 5 screenshots in place of the placeholders, then alt text + Rank Math SEO (title/meta description/focus keyword), then user-initiated Publish.

## 12. Images Attached, Alt Text, and SEO Set (2026-09-30)

First attachment attempt had images shifted one slot (Case 1-3 image duplicated 3x, Case 6/7 never inserted) — caught and fixed by resetting the post content back to plain-text placeholders via REST, then the user re-attached all 5 images correctly, verified this time by explicit case-number labels added to each placeholder's alt text.

Final image order confirmed via REST (post 69, media IDs 76-80): Case 1-3 → Case 4 → Case 5 → Case 6 → Case 7, matching the article's section order. Alt text set both in the media library and inline on each `<img>` tag (regex on the `wp-image-N` class, since alt precedes the class attribute in Gutenberg's markup — first attempt's regex assumed the wrong attribute order and silently no-op'd, caught by re-verifying via REST). Rank Math SEO set via `wp.data.dispatch('rank-math')` (title, meta description, focus keyword = "excel split comma separated values into rows"), confirmed persisted after a full page reload.

Draft (post ID 69) is now content + fixture + evidence + images + alt text + SEO complete. Only remaining step is user-initiated Publish.
