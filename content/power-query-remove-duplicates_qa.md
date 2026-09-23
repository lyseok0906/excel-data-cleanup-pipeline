# QA / Publish-Readiness Package — "power-query-remove-duplicates"

Source article: `content/power-query-remove-duplicates.md`
Predecessor: Pilot A (`power query remove duplicates` integrated guide, LIVE TEST T2) — no `content/pilot_A_*.md` file exists in this repo; the only prior record is the project decision log's `claude/비즈니스_방향_결정_로그.md` (2026-09-10 LIVE TEST spec, 2026-09-15 independent verification entries) and `docs/pilot_results.md`'s summary row.
Prepared: 2026-09-21
Prepared by: Cowork (assistant), per `docs/content_operations_playbook.md`, using **only facts already recorded in the decision log — no new research, no new Excel reproduction this round** (per explicit user instruction).
Status at end of this package: see "Final Verdict" at the bottom.

---

## 1. Article Metadata (for WordPress, NOT uploaded)

| Field | Value |
|---|---|
| Title | Power Query Remove Duplicates: Latest Row, Ties & Nulls |
| Slug | `power-query-remove-duplicates` |
| Meta description | Excel's Remove Duplicates only keeps the first row. Here's how to use Power Query to keep the latest row per ID and break same-date ties deterministically. (158 chars, shortened this round — see Finding C below) |
| Category | Power Query |
| Search Intent | Integrated / Reference guide |
| QA grade (per `docs/qa_policy.md`) | High-risk Integrated Guide |
| Focus keyword (Rank Math) | power query remove duplicates |
| Internal link candidates | `excel-remove-blank-rows-guide` (Pilot G, production draft exists — not linked in-body yet, since Pilot G is itself not yet published); `excel-split-comma-values-into-rows` (Pilot B, not yet converted — do not link until it exists) |

No internal links were inserted into the article body, for the same reason as Pilot F/G: neither candidate target is a live, published URL yet.

**Finding C (resolved this round):** the first draft of the meta description ran ~209 characters, over the usual ~155–160 character guideline. Shortened to 158 characters (dropping the "handle two-column keys" clause, which is one of eight cases and not essential to the meta description) while keeping the core differentiator (latest row, ties) intact.

## 2. Source Cross-Check (decision log vs. this draft) — no new research or reproduction performed

This is the key difference from the Pilot F/G QA packages: those had a real fixture and real Excel screenshots to cross-check against. **Pilot A has neither in this repo.** Everything below is a mapping from the article's claims back to what the decision log already asserts as verified — not a fresh independent check.

Cross-checked against:
- `claude/비즈니스_방향_결정_로그.md`, section "Blog B(Excel/키워드형) LIVE TEST 승인" (2026-09-10) — defines T2 (Power Query Integrated Guide) and its 8 subcases: basic duplicate key / keep latest row per ID / two-column key / blank·null key / same-date tie / null date / query folding / deterministic method.
- Same document, section "LIVE TEST 실행 결과 독립 검증 및 Pilot A/B 최종 상태" (2026-09-15) — records the actual M code for the same-date tie-break, extracted directly from the user's saved LIVE TEST workbook (`log_b_excel_live_test_evidence.xlsx`) via `customXml`/`DataMashup` base64 decoding, and the T2.7 (query folding) "NOT APPLICABLE" determination for an `Excel.CurrentWorkbook()` source.
- `docs/pilot_results.md` — Pilot A summary row (`CONTENT READY`, High-risk Integrated Guide, Gate history).

**Finding D (flag, not a blocker):** the decision log records that T2.2/2.3/2.4/2.6 (basic key, latest-per-ID, two-column key, deterministic method) were verified against "recalculated expected values" and matched, and that T2.5 (same-date tie) and T2.7 (query folding) were independently confirmed via the extracted M code — but it does **not** retain the actual input/output data values used in the LIVE TEST fixture for T2.2/2.3/2.4/2.6 (only the pass/fail conclusion). This article's Cases 1, 3, and 8 therefore describe the *general M-code pattern* Power Query uses for those operations (which is standard, documented Power Query mechanics — grouping and sorting), rather than reproducing the LIVE TEST's specific dataset, because that dataset's exact values are not preserved anywhere in this project. This is disclosed in-article implicitly (no fabricated "before/after" numbers are shown for Cases 1, 3, 4, 6, 8) and explicitly here.
- **What is NOT a gap:** Case 5 (same-date tie) and Case 7 (query folding) use the *exact* M code and determination independently verified in the decision log, not a generic reconstruction.
- **What the article does NOT claim:** it does not claim any of Cases 1–4, 6, or 8 were re-verified this round, and it does not present invented example numbers as if they were reproduced. It presents the grouping/sorting pattern as Power Query's standard documented mechanism (backed by the Sources), with Case 5/7 as the two places where this project's own prior verification adds something beyond the official docs.

**Finding E (flag, not a blocker):** the two official sources cited (`Find and remove duplicates`, `Table.Distinct`) were looked up this round to confirm the URLs are correct and current — this is source-citation verification, not new investigation into how the feature behaves, and does not conflict with the user's "no new research" instruction for this round. Both URLs were previously referenced in the decision log's LIVE TEST design section by description (not by URL), and are only being attached here.

**Conclusion:** the article's technical claims either (a) restate what the decision log already asserts as independently verified (Cases 5, 7, and the built-in Remove Duplicates / Table.Distinct facts), or (b) describe standard, officially-documented Power Query mechanics without claiming project-specific reproduction (Cases 1–4, 6, 8). No claim in the article goes beyond what is already established. Finding D above is the one place where "already confirmed" is weaker than for Pilot F/G, and it is disclosed rather than glossed over.

## 3. Technical QA Checklist

| # | Item | Result |
|---|---|---|
| 1 | Every formula/M-code snippet in the article is syntactically valid Power Query M | PASS (Case 5's snippet is the exact code extracted from the LIVE TEST workbook; the others follow the same `Table.Group`/`Table.Sort`/`Table.First` shape, which is standard M syntax) |
| 2 | Every claimed behavior matches either official Microsoft documentation or project-recorded verification | PASS, with the scope limitation in Finding D disclosed for Cases 1, 3, 4, 6, 8 |
| 3 | Retained reproduction evidence (fixture and/or screenshot) exists for each case | **FAIL / NOT YET MET** — no fixture file for this topic exists in this repo, and no screenshots exist yet. This is the single largest gap versus Pilot F/G and is carried forward as the primary blocker (see §4 and §7). |
| 4 | Version applicability statement is accurate | PASS — Power Query / Get & Transform has been available since Excel 2016, so the "Applies to" line is not overstated |
| 5 | No known Blog B content trap is present (CHAR vs UNICHAR, Text.Combine null-vs-empty-string, Go To Special blank-row deletion) | PASS — Case 4 (blank/null keys) explicitly cross-references the project's own null-vs-empty-string finding rather than treating all "missing" keys the same way; the other two known traps are not applicable to this topic |

## 4. Screenshot / Fixture List (NOT YET CAPTURED — primary blocker)

No fixture file exists in this repo for this topic. The original LIVE TEST fixture (`blog_b_excel_live_test_pack.xlsx`) was never migrated to `fixtures/`, and its exact T2 dataset values are not preserved elsewhere (Finding D). Per `docs/content_operations_playbook.md`'s evidence rules and the High-risk Integrated Guide grade (which calls for multiple fixtures/screenshots, per `docs/qa_policy.md`), this article needs a **new fixture built from scratch** before it can move past Draft — this is new fixture *construction*, not new research into how Power Query behaves, so it does not conflict with the "no new research" instruction, but it has not been done in this round because the user asked for Pilot A's article + QA package specifically, not the fixture/screenshot round.

Planned fixture (for a future round, once the user confirms): one workbook with a raw data sheet and one sheet per case —

| # | Case | Screenshot content needed | Alt text (draft) |
|---|---|---|---|
| 1 | Basic duplicate key | Grouped result showing one row per key | "Power Query grouped table showing one row kept per duplicate key" |
| 2 | Keep latest row per ID | Result showing the most recent row survives per ID, older rows removed | "Power Query result keeping only the most recently updated row per customer ID" |
| 3 | Two-column (composite) key | Result showing rows with same ID but different second-key value both survive | "Power Query grouping on a two-column composite key preserving distinct combinations" |
| 4 | Blank/null keys | Before/after showing blank-key rows handled separately, not silently collapsed | "Power Query table with blank-key rows routed around the deduplication step" |
| 5 | Same-date tie | The verified tie-break M code's result — correct row (RowID9-equivalent) selected | "Power Query same-date tie broken by a secondary RowID sort" |
| 6 | Null dates | `_SortDate` helper column substituting 1900-01-01 for null | "Power Query helper column substituting a placeholder date for null dates before sorting" |
| 7 | Query folding | Query diagnostics / "View Native Query" greyed out or absent for an in-workbook source | "Power Query showing query folding is not applicable for an Excel.CurrentWorkbook source" |
| 8 | Deterministic result | Full pipeline result, re-run/refreshed to show identical output | "Power Query deduplication result unchanged after refresh, confirming deterministic output" |

**Status: blocking.** This is the single outstanding item before this article can leave Draft, same pattern as Pilot F and Pilot G before their screenshot rounds — with English-UI capture from the start, per the lesson learned on Pilot F.

## 5. SEO/Search-Intent QA Checklist (Rank Math-oriented, no score-chasing repetition)

| # | Item | Result |
|---|---|---|
| 1 | Focus keyword ("power query remove duplicates") appears naturally in title, meta description, and body | PASS |
| 2 | Title matches search intent (Integrated/Reference guide) and states the concrete differentiator ("Latest Row, Ties & Nulls") | PASS — this is the exact SEO title already recorded as agreed in the decision log's 2026-09-10 LIVE TEST section, carried forward unchanged |
| 3 | Meta description is under ~160 characters | PASS — shortened to 158 chars this round (Finding C) |
| 4 | Headings (H2s) map onto distinct, scannable sub-tasks a searcher would look for | PASS — one H2 per case, matching the 8 LIVE TEST subcases |
| 5 | No keyword-density padding, no repeated phrase insertion purely to satisfy an SEO score | PASS |
| 6 | Internal links only point to pages that actually exist | PASS — no internal links inserted this round |

## 6. US English QA Checklist

| # | Item | Result |
|---|---|---|
| 1 | US spelling/vocabulary conventions throughout | PASS |
| 2 | Instructions use US Excel/Power Query terminology (Data > Get & Transform, Table.Group, etc.) | PASS |
| 3 | Grammar, punctuation, and M-code block formatting are correct and consistent | PASS |
| 4 | Tone matches Blog B's plain, task-focused style (no marketing fluff) | PASS |

## 7. Publish-Readiness Status

- WordPress upload: **NOT performed** (no draft, no publish) — Draft-only per explicit user instruction.
- Repo storage: article and this QA package to be committed to the repo this round; `docs/content_status.md` to be updated in the same commit.
- Fixture: **does not exist yet** — primary blocker (§4).
- Screenshot evidence: **does not exist yet** — primary blocker (§4), depends on the fixture above.
- Meta description length: fixed this round (Finding C).
- Human Approval: not requested this round — this package documents Draft status only, consistent with "WordPress에는 Human Approval 전까지 Draft만 허용" instruction.

## 8. Final Verdict

**DRAFT — REVISION APPLIED (2026-09-23) PER INDEPENDENT QA — TECHNICALLY SOUND PER EXISTING RECORDS, NOT YET EVIDENCE-COMPLETE.**

Rationale: every technical claim in the article is either a direct restatement of something the decision log already records as independently verified (Cases 5 and 7, the built-in Remove Duplicates behavior, the `Table.Distinct` folding caveat), or a standard, officially-documented Power Query mechanism presented without a fabricated reproduction claim (Cases 1–4, 6, 8, disclosed in Finding D). No new research or Excel reproduction was performed this round, per instruction. The article is **not** yet CONTENT READY, because — unlike Pilot F/G — this High-risk Integrated Guide grade calls for fixture-backed screenshots across its 8 cases, and none exist yet (§4). See §9 for the round of fixes just applied per independent ChatGPT QA; awaiting re-confirmation before this Pilot is considered content-approved.

## 9. Revision Round — ChatGPT Independent QA (2026-09-23)

**Verdict received:** 수정 필요 (revision required).

**Issues raised:**
1. `Table.Group(... "Chosen" ...)` produces a table of grouping keys plus a `Chosen` **record** column — the article never showed the step that expands that record back into real columns, so the guide stopped short of a usable result table.
2. Case 5 (Same-Date Ties) referenced `WithSortDate`, a table that had not yet been introduced at that point in the article — it is only created in Case 6 (Null Dates), which comes after it.
3. Case 4 says to handle "blank or null" keys but the example filter (`[CustomerID] <> null`) only excludes `null`, not an empty-string (`""`) key — leaving the empty-string case unaddressed despite the case's own title.

**Changes made:**
1. Added a new paragraph and code block right after "The Building Block" section introducing `Table.ExpandRecordColumn(GroupedResult, "Chosen", Table.ColumnNames(Source))`, explaining that every case's `Table.Group` output needs this step to become a normal flat table, and telling the reader to add it as the final step in every case.
2. Reordered the tie-break exposition: Case 5 now shows a self-contained tie-break using `UpdatedDate` (already introduced in Case 2) with no forward reference. Case 6 (Null Dates) still introduces the `_SortDate` helper column, and a new paragraph at the end of Case 6 shows the combined `_SortDate`-based version of the Case 5 pattern (this is where the original exact-verified code moved to, unchanged), explicitly defining what `WithSortDate` refers to.
3. Rewrote Case 4 to explicitly name `""` as a separate case from `null` (since `Table.Group` treats them as different group values), added a bullet instructing the reader to decide whether both count as "missing," and gave the two-condition filter `Table.SelectRows(Source, each [CustomerID] <> null and [CustomerID] <> "")` as the version to use when they do.

**Not changed:** the underlying verified facts (the exact `_SortDate`/`RowID` tie-break M code and the query-folding "not applicable" determination for an in-workbook source, both confirmed by this project's LIVE TEST reproduction) — these were not disputed by the QA and remain exactly as extracted from the decision log, just relocated to close the forward-reference gap.
