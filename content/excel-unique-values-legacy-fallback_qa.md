# QA / Publish-Readiness Package — "excel-unique-values-legacy-fallback"

Source article: `content/excel-unique-values-legacy-fallback.md`
Predecessor: Pilot E (`Excel 2021 UNIQUE 대체 legacy fallback`, Simple Task grade) — no `content/pilot_E_*.md` file exists in this repo; the only prior record is `claude/비즈니스_방향_결정_로그.md` (2026-09-15 "Pilot C/D/E 실측 결과 및 Gate 판단" section, plus the earlier correction that Excel 2021 does support `UNIQUE()` natively) and `docs/pilot_results.md`'s summary row.
Prepared: 2026-09-23
Prepared by: Cowork (assistant), per `docs/content_operations_playbook.md`, using **only facts already recorded in the decision log — no new research, no new Excel reproduction this round** (per standing user instruction for Pilot A–E conversions). Official Microsoft doc URLs (UNIQUE, INDEX, MATCH, COUNTIF) were looked up this round for citation purposes only.

---

## 1. Article Metadata (for WordPress, NOT uploaded)

| Field | Value |
|---|---|
| Title | Get Unique Values in Excel 2019 and 2016 (No UNIQUE Function) |
| Slug | `excel-unique-values-legacy-fallback` |
| Meta description | UNIQUE() isn't available in Excel 2019 or 2016. Here's the array-formula fallback that extracts unique values in first-appearance order, no add-ins needed. (156 chars) |
| Category | Formulas |
| Search Intent | Comparison / Method choice (fallback for older versions) |
| QA grade (per `docs/qa_policy.md`) | Simple Task |
| Focus keyword (Rank Math) | excel unique values without unique function |
| Version scope | `UNIQUE()` native: Microsoft 365, Excel 2024, Excel 2021. Fallback article scope: Excel 2019, Excel 2016 only — **note the decision-log correction below** |
| Internal link candidates | `power-query-remove-duplicates` (Pilot A, production draft exists, not yet published); `excel-trim-not-removing-nonbreaking-space` (Pilot C, production draft exists, not yet published) — **neither linked in-body**, since neither is a live published URL yet |

## 2. Important Correction Already Applied From the Decision Log

The original Pilot E design brief (per the project's own naming, "Pilot E — Excel 2021 UNIQUE 대체 legacy fallback") initially assumed Excel 2021 did **not** support `UNIQUE()`. The decision log records a subsequent correction: Microsoft's official `UNIQUE()` documentation lists Microsoft 365, Excel 2024, **and Excel 2021** as supported versions. A Microsoft Q&A post once cited as evidence that "UNIQUE/FILTER don't appear in Excel 2021" was later found to be a user-profile/installation issue, not a genuine version gap, and the decision log explicitly says not to use that post as evidence. Fallback scope was narrowed to **Excel 2019 and 2016 only**.

This article is written to reflect that correction from the start — the title, meta description, and version-scope statement all say "Excel 2019 and 2016," not "Excel 2021," and the article includes an explicit "Check Your Version First" section warning readers not to assume Excel 2021 lacks `UNIQUE()`. This avoids repeating the mistake the decision log already caught once.

## 3. Claim-by-Claim Evidence Map (no new research or reproduction performed this round)

| # | Claim in article | Evidence source | Status |
|---|---|---|---|
| 1 | `UNIQUE()` is supported in Microsoft 365, Excel 2024, and Excel 2021 (not just Microsoft 365) | [UNIQUE function](https://support.microsoft.com/en-us/office/unique-function-c5ab87fd-30a3-4ce9-9d1a-40204fb85e1e) — Microsoft Support | Official doc |
| 2 | The array formula `=IFERROR(INDEX($A$2:$A$9, MATCH(0, COUNTIF($C$1:C1, $A$2:$A$9), 0)), "")`, entered with Ctrl+Shift+Enter and filled C2:C6, against source data `Apple, Banana, Apple, Cherry, Banana, Date, Elderberry, Cherry` in A2:A9, produces `Apple, Banana, Cherry, Date, Elderberry` (5 unique values, first-appearance order) | Decision log, Pilot E `[Observed]` — direct reproduction in Excel, exact match to expected output | **Project-verified reproduction** |
| 3 | General behavior of `INDEX`, `MATCH`, and `COUNTIF` individually | [INDEX](https://support.microsoft.com/en-us/office/index-function-a5dcf0dd-996d-40a4-a822-b56b061328bd), [MATCH](https://support.microsoft.com/en-us/excel/functions/match-function), [COUNTIF](https://support.microsoft.com/en-us/excel/get-started/use-the-countif-function-in-microsoft-excel) — Microsoft Support | Official docs |
| 4 | The combined INDEX/MATCH/COUNTIF/IFERROR pattern as a technique for extracting unique values is well-known but not itself the subject of one official Microsoft page | Article states this explicitly rather than implying the combined technique itself is an official Microsoft recommendation | **Disclosed accurately** — the individual functions are officially documented; the specific combination is a community-standard technique that this project independently verified by reproduction, not by finding an official page describing this exact formula |

**Conclusion:** the version-scope claim (the one place earlier project work got something wrong) is backed directly by official Microsoft documentation and explicitly corrected from the original Pilot E framing. The formula's behavior is backed by a project-verified reproduction with an exact, checkable expected output. The individual building-block functions are backed by official docs. The one place this article is careful not to overclaim is calling the combined formula "official" — it isn't a single documented Microsoft technique, and the article says so.

## 4. Technical QA Checklist

| # | Item | Result |
|---|---|---|
| 1 | The array formula is syntactically valid and was reproduced exactly as written | PASS — matches the decision log's `[Observed]` record verbatim |
| 2 | Every claimed behavior matches either official Microsoft documentation or project-recorded verification | PASS |
| 3 | Retained reproduction evidence (fixture and/or screenshot) exists | **Fixture created (2026-09-28), verified via LibreOffice recalculation** — screenshots still pending, see §5/§7. |
| 4 | Version applicability statement is accurate | PASS — this is the one Pilot where an earlier version claim was found wrong and corrected; this article reflects the corrected scope (Excel 2019/2016 fallback, not Excel 2021) throughout, and explicitly calls out the correction so a reader on Excel 2021 doesn't reach for an unnecessary workaround |
| 5 | No known Blog B content trap is present | PASS — none of the three standing traps (CHAR/UNICHAR, null vs "", Go To Special blanks) apply to this topic |

## 5. Fixture and Screenshot Requirements (NOT YET CAPTURED — primary blocker)

No fixture exists in this repo for this topic. Planned fixture (for a future round): one workbook with the exact source list used in the original reproduction (`A2:A9` = Apple, Banana, Apple, Cherry, Banana, Date, Elderberry, Cherry) and the array formula filled down C2:C9 (filling a couple of rows past the expected 5 results, to show the `IFERROR` blank-not-error behavior once results run out).

| # | Scenario | Screenshot content needed | Alt text (draft) |
|---|---|---|---|
| 1 | Formula entry as an array formula | Formula bar showing the formula wrapped in `{ }` curly braces after Ctrl+Shift+Enter | "Array formula in Excel shown with curly braces after Ctrl+Shift+Enter entry" |
| 2 | Filled-down result | C2:C6 showing the five unique values in first-appearance order | "Legacy array formula extracting unique values in the order they first appear" |
| 3 | Past-the-end behavior | C7:C9 showing blank cells (not error values) once all unique values are extracted | "IFERROR showing blank cells instead of errors once every unique value has been extracted" |
| 4 | Version check | `UNIQUE()` entered directly in Excel 2021, showing it works natively (not `#NAME?`) | "UNIQUE function working natively in Excel 2021, confirming no fallback is needed there" |

**Status: fixture created (2026-09-28)** — `fixtures/excel-unique-values-legacy-fallback_fixture.xlsx`. Sheet `Unique_Fallback` has the exact source list (`A2:A9` = Apple, Banana, Apple, Cherry, Banana, Date, Elderberry, Cherry), the legacy CSE array formula filled down `C2:C9` (each row's `$C$1:C{n-1}` reference grown individually), and `=UNIQUE(A2:A9)` in `E2` for the version-check screenshot. Verified via LibreOffice headless recalculation: `C2:C6` = Apple, Banana, Cherry, Date, Elderberry exactly, `C7:C9` = blank (not error values), and `UNIQUE()` computed without `#NAME?`. A `Capture_Notes` sheet gives cell-by-cell instructions for the 4 screenshots below, including a note to re-enter `C2` with Ctrl+Shift+Enter live in Excel to confirm the curly-brace behavior (a file-stored array formula flag isn't the same as a live CSE entry). **Still blocking:** English-UI screenshots have not yet been captured.

## 6. SEO/Search-Intent QA Checklist

| # | Item | Result |
|---|---|---|
| 1 | Focus keyword appears naturally in title, meta description, and body | PASS |
| 2 | Title matches search intent (a fallback for specific older versions) and doesn't overclaim scope | PASS — title specifies "Excel 2019 and 2016," not a general "get unique values" claim that would misleadingly suggest UNIQUE() doesn't exist elsewhere |
| 3 | Meta description is under ~160 characters | PASS (156 chars) |
| 4 | Headings (H2s) map onto distinct, scannable sub-tasks (check your version, the formula, how it works) | PASS |
| 5 | No keyword-density padding | PASS |
| 6 | Internal links only point to pages that actually exist | PASS — none inserted this round |

## 7. US English QA Checklist

| # | Item | Result |
|---|---|---|
| 1 | US spelling/vocabulary conventions throughout | PASS |
| 2 | Instructions use standard Excel formula/menu terminology (Ctrl+Shift+Enter, array formula/CSE formula both mentioned for searchability) | PASS |
| 3 | Grammar, punctuation, and formula/code-block formatting are correct and consistent | PASS |
| 4 | Tone matches Blog B's plain, task-focused style | PASS |

## 8. Publish-Readiness Status

- WordPress upload: **NOT performed** — Draft-only, per instruction (public publish requires separate user approval).
- Repo storage: article and this QA package to be committed to the repo this round; `docs/content_status.md` updated in the same commit.
- Fixture: **created (2026-09-28)** — `fixtures/excel-unique-values-legacy-fallback_fixture.xlsx`, verified via LibreOffice headless recalculation (see §10).
- Screenshot evidence: **still not captured** — only remaining blocker; cell-by-cell capture plan is embedded in the fixture's `Capture_Notes` sheet.
- Residual risk: none beyond the standard screenshot gap — the version-scope correction (the one thing earlier project work got wrong on this topic) has already been applied throughout this article.
- Human Approval: not requested this round.
- Independent QA: not yet submitted to ChatGPT this round (Pilot A–D each went through this step; recommend the same for Pilot E before considering it fully confirmed, consistent with the pattern established this session).

## 9. Final Verdict

**DRAFT — TECHNICALLY SOUND PER EXISTING RECORDS AND OFFICIAL DOCS, NOT YET EVIDENCE-COMPLETE.**

Rationale: the article's central reproduced claim (the array formula's exact output against the documented test dataset) is a direct restatement of a project-verified reproduction already recorded in the decision log (Pilot E, PASS, no re-verification needed per the lightweight model). The version-scope claim — the one place earlier work on this topic was initially wrong — is corrected throughout and backed by official Microsoft documentation. The individual building-block functions are backed by official docs; the combined technique is honestly described as a well-known but not officially-documented-as-such pattern. No new research or Excel reproduction was performed this round. The article is **not** yet fully evidence-complete: the fixture now exists and is verified (§10), but English-UI screenshots have not yet been captured. Recommend independent ChatGPT QA before considering this Pilot past "content approved, screenshots pending."

## 10. Fixture Creation (2026-09-28)

Built `fixtures/excel-unique-values-legacy-fallback_fixture.xlsx` (sheet `Unique_Fallback`) with the exact source list from the decision log (`A2:A9`) and the legacy CSE array formula filled down `C2:C9`, plus `=UNIQUE(A2:A9)` in `E2` for the Excel-2021-native version-check screenshot.

Each row's array formula was written individually via `openpyxl.worksheet.formula.ArrayFormula` with its own growing `$C$1:C{n-1}` reference (not a single copy-pasted formula), matching how the article describes it being filled down top-to-bottom.

**Verification note:** `UNIQUE` is a post-2007 function and needed the `_xlfn.UNIQUE` prefix in the raw formula (same issue caught and fixed during Pilot C's fixture build) to avoid `#NAME?` when opened outside of Excel's own save round-trip.

Verified via `soffice --headless --convert-to xlsx` recalculation (Linux/LibreOffice sanity check, not the target Windows/Excel environment): `C2:C6` computed to exactly `Apple, Banana, Cherry, Date, Elderberry` (matching the decision log's original reproduction), `C7:C9` computed to blank (not `#N/A`), confirming `IFERROR` behaves as the article describes. `E2` (`UNIQUE(A2:A9)`) computed without `#NAME?`, confirming the formula is syntactically valid; LibreOffice's handling of the dynamic-array spill into `E3:E6` was inconclusive in this cross-platform check (not the real target — real Excel 2021+ on the user's machine is what actually confirms scenario 4), so that screenshot should still be captured and read plainly rather than assumed.

A `Capture_Notes` sheet in the workbook gives the exact cell references, expected formula-bar contents, and draft alt text for each of the 4 required screenshots, plus a reminder to re-enter `C2` live with Ctrl+Shift+Enter to confirm the curly-brace CSE display, since a file-stored array-formula flag isn't the same as Excel's live entry behavior.

**Remaining blocker:** English-UI screenshot capture in Excel, per the `Capture_Notes` sheet.

## 11. Screenshot Capture Confirmed (2026-09-29)

User captured all 4 required screenshots in Excel on the target machine (Korean-language Windows regional settings, English display language), using `fixtures/excel-unique-values-legacy-fallback_fixture.xlsx`. Saved to `evidence/excel-unique-values-legacy-fallback/`:

| # | File | Cell / formula shown | Measured result |
|---|---|---|---|
| 1 | `01-array-formula-curly-braces.png` | C2, `{=IFERROR(INDEX($A$2:$A$9, MATCH(0, COUNTIF($C$1:C1, $A$2:$A$9), 0)), "")}` | Curly braces present, confirming a valid CSE array formula |
| 2 | `02-unique-values-first-appearance-order.png` | C2:C6 | Apple, Banana, Cherry, Date, Elderberry — matches expected order exactly |
| 3 | `03-iferror-blank-not-error.png` | C7:C9 | Blank cells, no `#N/A` — confirms `IFERROR` behavior once every value is extracted |
| 4 | `04-unique-function-native-excel2021.png` | E2:E6, `=UNIQUE(A2:A9)` | Spilled correctly to Apple, Banana, Cherry, Date, Elderberry, confirming `UNIQUE()` works natively on this Excel version |

**Finding during capture (worth noting for future fixtures):** the first attempt at screenshot 4 showed `=@UNIQUE(A2:A9)` in the formula bar — Excel had inserted the implicit-intersection `@` operator and returned only "Apple" instead of spilling, because the formula was written into the xlsx by openpyxl (a non-Excel tool) rather than typed live in a dynamic-array-aware Excel session. This is a real, documented Excel compatibility behavior (older-style formula entry gets `@` prepended to preserve single-value semantics), not a bug in the article's claim. **Fix:** the user deleted E2 and retyped `=UNIQUE(A2:A9)` directly in Excel, which then spilled correctly with no `@`. The corrected screenshot is what's saved as file 4 above. This is a useful thing to keep in mind for any future fixture involving dynamic-array functions (UNIQUE, SORT, FILTER, etc.) written via openpyxl: the formula may need to be re-typed live in Excel rather than trusted as-authored.

**Technical QA item 3 (reproduction evidence) status: now PASS.** All 4 screenshots match the article's claims exactly.

**Final Verdict updated:** DRAFT — CONTENT APPROVED, FIXTURE + SCREENSHOTS COMPLETE. Ready for WordPress Draft creation, pending user go-ahead (same protocol as Pilot C/G).

## 12. WordPress Draft Created (2026-09-29)

Created via REST API through the already-authenticated Claude Browser session (cookie + nonce, no credentials entered), same method as Pilot C/G:

- **Post ID 44**, slug `excel-unique-values-legacy-fallback`, status `draft`.
- Category: created new category "Formulas" (id 5) via REST — did not exist yet on this site.
- Content: full article converted to Gutenberg blocks matching `content/excel-unique-values-legacy-fallback.md` exactly, with 4 bolded `[IMAGE N — filename.png]` placeholder paragraphs marking insertion points:
  1. `04-unique-function-native-excel2021.png` — after "Check Your Version First"
  2. `01-array-formula-curly-braces.png` — after the CSE entry instructions in "The Legacy Array Formula"
  3. `02-unique-values-first-appearance-order.png` — after the reproduction result paragraph, same section
  4. `03-iferror-blank-not-error.png` — after the IFERROR explanation in "How the Formula Works"
- Excerpt set to the meta description.
- Rank Math SEO fields set via `wp.data.dispatch('rank-math')`: focus keyword `excel unique values without unique function`, SEO title matching the article title, meta description matching the excerpt. Saved via `core/editor` `savePost()`, verified persisted after a full page reload.
- Post status confirmed `draft` before and after the SEO save.

**Remaining steps (same protocol as Pilot C/G):** user attaches the 4 images directly in the already-open editor; Cowork then sets alt text on each image (media library + inline `<img>`) using the exact wording from §5/§11; status stays Draft until a separate explicit publish decision.

## 13. Images Attached and Alt Text Set (2026-09-29)

User attached the 4 screenshots directly in the editor (post ID 44). One image (04-unique-function-native-excel2021.png) was initially left as an empty image block with no file — caught via a REST check (imgCount 3, one `<img alt=""/>` with no src), reported to the user, and the user filled it in; verified again after via REST to confirm all 4 present with real media IDs (47–50) before proceeding.

- Alt text set on all 4 media library attachments via REST (`wp/v2/media/{id}`), using the exact wording from §5/§11.
- Alt text also injected into the inline `<img alt="">` attributes in post content (4/4 replacements), since media-library alt text does not propagate into already-inserted blocks — same method as Pilot C/G.
- Rank Math SEO fields were already set via the `rank-math` data store in §12, prior to this step.
- Post status confirmed `draft` throughout — the user clicked "Publish" once during the image-attachment step but did not complete the second pre-publish confirmation, so no unintended publish occurred this time (unlike Pilot C).
- **Current state: status `draft`, all content/images/alt text/SEO complete. Publish approval not yet given — awaiting separate explicit decision.**
