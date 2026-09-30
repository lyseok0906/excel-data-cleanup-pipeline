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

**DRAFT — CONTENT APPROVED (per ChatGPT independent QA, 2026-09-23, round 3) — PENDING FIXTURE / ENGLISH-UI SCREENSHOTS.**

Rationale: every technical claim in the article is either a direct restatement of something the decision log already records as independently verified (Cases 5 and 7, the built-in Remove Duplicates behavior, the `Table.Distinct` folding caveat), or a standard, officially-documented Power Query mechanism presented without a fabricated reproduction claim (Cases 1–4, 6, 8, disclosed in Finding D). No new research or Excel reproduction was performed this round, per instruction. Round 1 of independent QA (§9) fixed the missing expand step, the forward-reference ordering issue, and the incomplete blank-key guidance; round 2 (§10) fixed a correctness bug in the round-1 expand step itself. The article is content-approved; it is **not** yet CONTENT READY only because — unlike Pilot F/G — this High-risk Integrated Guide grade calls for fixture-backed screenshots across its 8 cases, and none exist yet (§4).

## 10. Revision Round 2 — ChatGPT Independent QA (2026-09-23)

**Verdict received:** 수정 1건 필요 (one fix required).

**Issue raised:** the round-1 expand step, `Table.ExpandRecordColumn(GroupedResult, "Chosen", Table.ColumnNames(Source))`, expands every field of the `Chosen` record — including `CustomerID`, which is already present as its own column from the `Table.Group` grouping step. Expanding it again would attempt to create a duplicate `CustomerID` column and error.

**Change made:** replaced the expand step with a version that excludes the grouping key column(s) before expanding:

```
KeyColumns = {"CustomerID"},
FieldsToExpand = List.Difference(Table.ColumnNames(Source), KeyColumns),
Table.ExpandRecordColumn(GroupedResult, "Chosen", FieldsToExpand)
```

Added an explanatory paragraph covering why the naive expand fails (duplicate column name) and how `List.Difference` avoids it, plus a note that Case 3's composite key means `KeyColumns` there should be `{"CustomerID", "OrderDate"}` instead of the single-column default.

**Not changed:** everything else in the article — the round-1 fixes (Case 5/6 reordering, Case 4's null/"" guidance) and all other case-specific M code were not disputed by this round of QA.

**Post-fix verdict (round 2):** Pilot A — DRAFT, content approved, fixture/English-UI screenshots pending (same status as Pilot B/C/D/E).

## 11. Revision Round 3 — ChatGPT Independent QA (2026-09-23)

**Verdict received:** 코드 표기 1건 수정 필요 (one code-formatting fix required); content otherwise approved.

**Issue raised:** the round-2 expand step was written as three lines —

```
KeyColumns = {"CustomerID"},
FieldsToExpand = List.Difference(Table.ColumnNames(Source), KeyColumns),
Table.ExpandRecordColumn(GroupedResult, "Chosen", FieldsToExpand)
```

— which is not valid, directly-runnable M. It reads like the body of a `let ... in` block, but the article never wraps it in one, so it cannot simply be pasted into the Advanced Editor as shown.

**Change made:** replaced it with a single, directly-runnable expression that inlines `List.Difference` as the third argument to `Table.ExpandRecordColumn`, with no intermediate step names or missing `let...in`:

```
Table.ExpandRecordColumn(
    GroupedResult,
    "Chosen",
    List.Difference(Table.ColumnNames(Source), {"CustomerID"})
)
```

The explanatory paragraph was kept (why the naive expand would collide on `CustomerID`, and why `List.Difference` avoids it), and the Case 3 composite-key note was updated to say "replace the last argument with `List.Difference(Table.ColumnNames(Source), {"CustomerID", "OrderDate"})` instead" rather than referring to a `KeyColumns` variable that no longer exists in this version.

**Not changed:** the underlying logic (which columns get excluded from the expand, and why) is identical to round 2 — this round only fixed how the code is presented so it can be copied and run as-is.

**Final verdict:** Pilot A — **DRAFT, CONTENT APPROVED, fixture/English-UI screenshots pending** (same status as Pilot B/C/D/E). No further content or code-correctness issues outstanding.

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

## 12. Fixture Creation (2026-09-29)

**Fixture file:** `fixtures/power-query-remove-duplicates_fixture.xlsx`

Unlike Pilot C/E (cell-formula fixtures), Pilot A's queries are Power Query M code, which openpyxl cannot author directly (Power Query definitions live outside the cell-formula model). The fixture therefore contains only the **raw source data** for each of the 6 distinct cases (Case 7 reuses Case 1's query; Case 8 reuses Case 6's query — no separate source needed for either), each as a named Excel Table so the M code can reference it via `Excel.CurrentWorkbook(){[Name="..."]}[Content]`:

| Sheet | Table name | Columns | Rows |
|---|---|---|---|
| Case1_Source | Case1Source | CustomerID, Amount | C1/100, C1/150, C2/200 |
| Case2_Source | Case2Source | CustomerID, UpdatedDate, Amount | C1/2024-01-10/100, C1/2024-01-15/120, C2/2024-02-01/200 |
| Case3_Source | Case3Source | CustomerID, OrderDate, Amount | C1/2024-01-10/100, C1/2024-02-10/150, C2/2024-03-01/200 |
| Case4_Source | Case4Source | CustomerID, Amount | C1/100, (blank)/999, (=""))/888, C2/200 |
| Case5_Source | Case5Source | CustomerID, UpdatedDate, RowID, Amount | C1/2024-01-10/1/100, C1/2024-01-15/2/150, C1/2024-01-15/3/160 |
| Case6_Source | Case6Source | CustomerID, OrderDate, RowID, Amount | C1/(blank)/1/100, C1/2024-02-01/2/150 |

A 7th sheet, `Instructions`, contains: the exact M code to paste into the Power Query Advanced Editor for each of the 6 cases, the expected result for each, step-by-step instructions for Case 7 (query folding check) and Case 8 (refresh determinism check), and the full 8-screenshot capture plan with draft alt text (matching §4's table).

**Defect found and fixed during fixture build — null vs. empty string, again:** the first build attempt wrote Case 4's row 3 `CustomerID` as a plain Python `""`. On reload, openpyxl round-tripped it back as `None`, identical to the true-blank row above it — openpyxl silently collapses an assigned empty string to a blank cell on write, so the two rows were no longer distinguishable, defeating the entire point of Case 4. This is the same null-vs-empty-string trap this project has hit before (Pilot D's Text.Combine finding; Pilot G's `a81010a` fixture fix), this time surfacing in fixture *authoring* rather than in the target formula. **Fix:** row 3's `CustomerID` is now written as the formula `=""` instead of a literal string constant. A formula-evaluated zero-length string is a genuine, distinct TEXT value in Excel's data model (data type `f`, confirmed via openpyxl `cell.data_type` after reload), whereas a literal empty string assigned through openpyxl is not representable at all — it collapses to blank. This also mirrors how a true empty string usually actually reaches a real workbook (a formula, an import, or a linked source), since typing into a cell and clearing it always leaves a true blank, never an empty string. The `Instructions` sheet note for Case 4 was updated to explain this to the user, and to flag that the cell will show blank until Excel recalculates it (which happens automatically on open, so no manual action is needed).

**Verification:** re-opened the saved fixture with openpyxl and confirmed:
- All 6 case sheets have their named Table (`Case1Source`–`Case6Source`) with the exact ref range and headers listed above.
- Case 4 has 4 data rows: row 1 CustomerID `"C1"`, row 2 CustomerID `None` (data type `n`, genuinely blank), row 3 CustomerID `=""` (data type `f`, a formula — evaluates to a true zero-length string once opened in Excel), row 4 CustomerID `"C2"` — matching the article's Case 4.
- No `#NAME?`-risk functions used anywhere in this fixture (Power Query M code lives outside the cell-formula model, so the `_xlfn.` prefix issue that affected Pilot C/E does not apply here).

LibreOffice headless recalculation was **not** used for this fixture, unlike Pilot C/E — there is no cell formula to check against an expected numeric/text result (Case 4's `=""` is trivial and needs no recalculation check), and LibreOffice cannot execute Power Query M code at all, so it offers no verification value for the actual case logic. Verification for Cases 1–8 will happen when the user builds each query in real Excel and the result table is screenshotted, per the plan in the `Instructions` sheet.

**Second defect found and fixed — Excel repair-dialog corruption:** after delivering the fixture to the user, opening it in real Excel triggered "We found a problem with some content... Do you want us to try to recover as much as we can?" Root cause: openpyxl wrote the `=""` formula cell (Case4 row 4, CustomerID) with no explicit cell type (defaults to numeric `"n"`) and an empty cached `<v></v>`, which mismatches the formula's actual string result — this type/value mismatch is exactly what Excel's repair heuristic flags. **Fix:** post-processed the saved xlsx (raw zip/XML patch, since openpyxl has no API to set a formula cell's cached type without also supplying a cached value) to change that cell to `<c r="A4" t="str"><f>""</f></c>` — declaring the correct string type and dropping the bogus empty cache so Excel recalculates it cleanly on open. Verified: zip integrity (`testzip()` → no errors) and every part parses as well-formed XML; the fixture-build script (`/tmp/build_fixture_a.py`) now performs this patch automatically after every save.

**Status:** fixture created, corruption defect fixed, and verified structurally (valid zip, well-formed XML, correct Tables and data). Screenshots (8, English UI) still required from the user — capture plan and M code walkthrough delivered in chat. WordPress Draft not yet created.

## 13. Fixture Rebuild — Corruption Persisted, Root Cause Reassessed (2026-09-29)

**Report from user:** after receiving the fixture-corruption fix in §12 (the `=""` cell's type/cached-value patch), Excel still showed the same "We found a problem with some content... Do you want us to try to recover as much as we can?" dialog on open, identically.

**Reassessment:** the persistence of the identical error after that patch means the `=""` cell's type mismatch was not the (or not the only) actual cause — that patch addressed a real but non-fatal inconsistency, not the trigger for Excel's repair prompt. The one feature in this fixture with no precedent in this project's prior fixtures (Pilot C/E used only cell formulas, no structural document features) is openpyxl's `Table` object (`xl/tables/table*.xml`, `tableParts`, per-sheet `_rels`) — six of them, one per case sheet. Rather than continuing to guess at which specific Table attribute Excel's parser objects to (with no access to real Excel to test against directly, and LibreOffice's Calc — the only local sanity-check tool available — being much more lenient about malformed OOXML than Excel and therefore not a reliable corroborating signal), the fixture was rebuilt to remove Excel Tables from the design entirely.

**Change made:** each case's source range is now registered as a workbook-level **Named Range** (`xl/workbook.xml` `<definedNames>`) instead of an Excel Table object. This is a much simpler OOXML construct — no separate `xl/tables/*.xml` parts, no `tableParts` element per worksheet, no additional per-sheet relationship files, no additional `[Content_Types].xml` overrides — eliminating the entire class of Table-serialization issues as a possible cause. `Excel.CurrentWorkbook(){[Name="Case1Source"]}[Content]` still resolves a named range exactly as it resolves a named table, so the M code's `Source` step is unchanged in principle, but because a named range (unlike a Table) carries no built-in header-row metadata, every case's M code now inserts one additional step right after `Source` is read:

```
RawSource = Excel.CurrentWorkbook(){[Name="Case1Source"]}[Content],
Source = Table.PromoteHeaders(RawSource, [PromoteAllScalars=true]),
```

— after which every case's M code is unchanged (all downstream steps still reference `Source`). The `Instructions` sheet and this walkthrough were updated accordingly for all 6 cases.

**Not changed:** the underlying case data (all 6 source ranges' values), the Case 4 `=""`-formula technique and its `t="str"` type fix from §12 (kept, still correct practice regardless of Table vs. named-range), and the M code logic after the `Source` step for every case.

**Verification:** re-opened the rebuilt fixture with openpyxl (all 6 named ranges present and pointing at the correct absolute ranges; Case 4's blank-vs-formula distinction intact) and re-ran the zip/XML integrity check (`testzip()` → no errors; every part parses as well-formed XML) and a LibreOffice headless round-trip (no errors). None of these tools can fully replicate Excel's own OOXML strictness, so **this needs the user to confirm it now opens cleanly in real Excel before screenshot capture proceeds** — if the repair dialog still appears, the next hypothesis to test is the `Font(bold=True)` header-row styling or the date-typed cells (Case 2/3/5/6), by removing them one at a time.

**Status:** fixture rebuilt without Excel Tables (named ranges instead), M code walkthrough updated for all 8 cases. Awaiting user confirmation that the file now opens without a repair prompt before screenshots are captured.

## 14. Fixture Re-saved Through LibreOffice — Corruption Resolved (2026-09-29)

**Report from user:** the named-range rebuild in §13 still produced the same Excel repair dialog on open.

**Diagnosis reached:** two independent openpyxl-only fixes (§12: the `=""` cell's declared type; §13: removing Table objects in favor of named ranges) both failed to stop the repair prompt, while every check available in this environment — zip integrity, well-formed-XML-per-part, and a LibreOffice open/convert round-trip — reported no problems both times. That gap means the corruption openpyxl is writing is something real Excel's OOXML parser enforces stricter than LibreOffice's reader does, and that this project has no way to detect directly (no real Excel available in this environment to test against). Rather than continuing to guess at further individual XML attributes, the fixture is now **re-saved through LibreOffice itself** as a final build step: after openpyxl writes and the `=""` cell patch is applied, the file is converted `xlsx -> xlsx` via `soffice --headless --calc --convert-to xlsx`, and that LibreOffice-written output — not the openpyxl output — is what ships. LibreOffice is a mature, independently-implemented OOXML writer with a very different code path from openpyxl's; asking it to re-emit the file is a practical way to normalize away whatever openpyxl-specific quirk Excel was rejecting, without knowing exactly which one it was.

**Verified the round-trip preserved everything:** re-opened the LibreOffice-written file with openpyxl and confirmed all 7 sheets, all 6 named ranges (correct ranges), Case 4's blank-vs-`=""`-formula distinction (data types `n` and `f` respectively, unchanged), Case 2's date cells (correct `datetime` values, type `d`), and the full 113-line Instructions sheet are all intact and unchanged in value. Zip integrity and XML well-formedness re-checked, both clean.

**Build script updated:** `/tmp/pilotA/build_fixture_a2.py` (superseding `/tmp/build_fixture_a.py` from §12/§13) now performs this LibreOffice re-save automatically as its last step, so any future regeneration of this fixture ships the same normalized output rather than raw openpyxl bytes.

**Status:** fixture rebuilt a third time; this version ships LibreOffice-normalized OOXML rather than raw openpyxl output. Still requires the user to confirm it opens cleanly in real Excel — that confirmation has not yet been received. If this *still* doesn't resolve it, the next thing to try is dropping the date-typed cells (Case 2/3/5/6) or the bold header styling to isolate whether either of those, not the corrupted-cell mechanism guessed at in §12, is the actual trigger.

## 15. Root Cause Found and Fixed — Instructions Sheet Section Headers (2026-09-30)

**Actual root cause, finally identified:** none of the three prior hypotheses (§12 Case 4 cell type, §13 Table vs named range, §14 raw openpyxl vs LibreOffice-resaved output) were the real cause. Excel's own repair log — obtained by testing the fixture under a brand-new filename, which let the user click "Yes" on the recovery prompt and see the actual repair report — stated plainly: **"Removed Records: Formula from /xl/worksheets/sheet7.xml part"**. Sheet 7 is `Instructions`, a plain-text sheet with no intended formulas at all.

The cause: every section header in the `Instructions` sheet was written as a literal string starting with `===`, e.g. `"=== Case 1 - Basic duplicate key ==="`. openpyxl's rule for detecting a formula is simply "the cell's string value starts with `=`" — it has no awareness that `===` is meant as a plain-text visual divider, not a formula prefix. All 8 case/section headers were written this way, so openpyxl silently wrote each one as a `<f>` (formula) element instead of a text cell. Excel then tried to evaluate `== case 1 - basic duplicate key ===` as a formula expression, which is not valid syntax, producing `#VALUE!` and triggering the "we found a problem with some content" repair dialog for the whole workbook on every open — regardless of what else the file contained. This explains why the corruption persisted identically across every rebuild (§12 Table version, §13 named-range version, §14 LibreOffice-resave version): all three carried this same broken Instructions sheet unchanged.

**Why the earlier isolated diagnostic tests (all passed) failed to catch this:** the diagnostic test files built to isolate the cause (dates-only, named-range-only, formula-only, all-data-combined, Instructions-only, and even a full 7-sheet recombination) all used a placeholder Instructions sheet with a short repeated intro paragraph for testing convenience — none of them included the actual `=== Case N ... ===` section headers from the real Instructions content. The bisection method was sound, but the reconstructed test cases didn't reproduce the exact real content, so the actual defect was never in the tested surface. The renamed-file test (`_fixture_v2.xlsx`, real content, new filename) was what finally surfaced it, once the user could see Excel's own repair log (a previously untried diagnostic — clicking "Yes" on the repair prompt instead of "No", which reveals exactly what Excel removed).

**Fix:** replaced all 8 `=== ... ===` section headers in the Instructions sheet with `-- ... --` (a plain-text divider that doesn't start with `=`). Verified by inspecting the raw sheet XML: sheet 7 now has zero `<f>` elements, while sheet 4 correctly still has exactly one (the intentional Case 4 `=""` formula, data type `f`, confirmed unaffected). Zip integrity and well-formed XML re-checked, clean.

**Not changed:** the underlying case data for all 6 cases, the Case 4 `=""` formula technique (this was correct all along and never the actual problem), the named-range structure from §13 (kept — it's simpler than Tables and there was never a real defect in it), and the LibreOffice re-save step from §14 (kept as a belt-and-suspenders safety net, though it was never the fix either).

**Lesson for future fixtures:** any plain-text content written into a cell via openpyxl — not just deliberate formulas — must be checked for a leading `=`, since openpyxl has no way to distinguish "this text happens to start with an equals sign" from "this is a formula." Section dividers, code comments, or any instructional text using `=` as a visual marker (banners, before/after diffs, etc.) need a different leading character.

**Status:** CONFIRMED FIXED — user reports the fixture now opens in real Excel with no repair dialog (2026-09-30). Fixture is complete and stable. Next step: user builds the 8 Power Query queries per the M code walkthrough (delivered in chat and in the Instructions sheet) and captures the 8 required screenshots (English UI). WordPress Draft not yet created.

## 16. Screenshots Captured and Verified — 8/8 (2026-09-30)

User built all 8 Power Query queries per the §15 M code walkthrough and captured/sent all 8 required screenshots. Each was checked against the case's expected result before approval:

1. **Case 1** — result table, 2 rows (C1/100, C2/200). Matches (C1's surviving Amount is unconstrained by this case).
2. **Case 2** — result table, C1 UpdatedDate 2024-01-15/Amount 120, C2/200. Matches — older C1 row correctly dropped.
3. **Case 3** — result table, all 3 rows preserved (C1 on two different OrderDates, C2). Matches — composite key correctly did not collapse the two C1 rows.
4. **Case 4** — result table, 4 rows: C1/100, C2/200, plus both blank-key rows (999, 888) kept separately (one shown as `null`, the other as a true blank cell — visually confirms `null` and `""` were not collapsed into a single row). Matches.
5. **Case 5** — result table, 1 row: C1, UpdatedDate 2024-01-15, RowID 3, Amount 160. Matches — same-date tie correctly broken by RowID descending.
6. **Case 6** — `WithSortDate` intermediate step (not the final result), showing the `_SortDate` column with the null `OrderDate` row substituted to 1900-01-01 and the real-date row unchanged. Matches.
7. **Case 7** — right-click context menu on a query built on `Excel.CurrentWorkbook()` (the user's surviving query at time of capture was the Case 6 query, not Case 1 — accepted as equivalent evidence since the query-folding behavior being demonstrated depends on the source type, `Excel.CurrentWorkbook()`, not on which case's transformation logic sits on top of it). Note: in this Excel build, "View Native Query" does not appear at all in the menu (rather than appearing greyed out) for a non-foldable in-workbook source — this absence is itself the evidence Case 7 is documenting, and the walkthrough text should be read as "greyed out or absent" going forward.
8. **Case 8** — same query (Case 6) refreshed; result unchanged (CustomerID C1, RowID 2, Amount 150, OrderDate/SortDate correctly displaying as 2024-02-01 after the user reformatted the date columns for readability). Matches.

**Process note:** during capture, the user's Power Query queries for Cases 1–5 were lost (each new Blank Query was left named "Query1" by default, so later queries appear to have overwritten earlier connection entries — only one query, "Query1" holding the Case 6 logic, remained by the time Cases 7–8 were attempted). This did not block completion since Cases 1–6's result screenshots had already been captured and approved before this was discovered, and Cases 7–8 only need any query built on the same source type. **Lesson for future pilots with multiple Power Query cases in one fixture: instruct the user to rename each query immediately after creating it** (Query Settings pane → Name field) before moving to the next case, to avoid this.

**Status:** all 8 screenshots captured and verified against expected results. Fixture and screenshots complete. Next: WordPress Draft creation (title/content/category/meta via REST, images attached manually by the user per their stated preference — same pattern as Pilots C/E/G).

## 17. WordPress Draft Created (2026-09-30)

Following the same pattern as Pilots C/E/G: title, content, category and Rank Math SEO meta set via REST/`wp.data`, images to be attached manually by the user.

- **Post ID:** 56
- **URL:** https://cleansheethq.com/?p=56
- **Status:** draft
- **Category:** "Power Query" (id 6) — newly created; did not exist before this pilot.
- **Content:** full article converted to Gutenberg blocks (headings, paragraphs, code blocks, lists), with 8 `[IMAGE N — description]` placeholder paragraphs marking where each of the 8 verified screenshots (§16) goes.
- **Rank Math SEO:** set via `wp.data.dispatch('rank-math')` (REST doesn't expose Rank Math postmeta on this site) — focus keyword "power query remove duplicates", SEO title matching the H1, meta description matching the article's `meta_description` frontmatter. Saved via `core/editor.savePost()`, confirmed via full page reload + re-read (status remained `draft`).
- **Not yet done:** image attachment (user will attach manually), alt text, and publish (pending explicit user approval, as with all prior pilots).

**Status:** Draft ready for the user to attach the 8 images.
