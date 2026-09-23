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
| 3 | Retained reproduction evidence (fixture and/or screenshot) exists | **FAIL / NOT YET MET** — no fixture file for this topic exists in this repo, and no screenshots exist. Same primary blocker pattern as Pilot A/B/C/D. |
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

**Status: blocking**, same as Pilot A/B/C/D. English-UI capture required from the start.

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
- Fixture: **does not exist yet** — primary blocker (§5).
- Screenshot evidence: **does not exist yet** — primary blocker (§5), depends on the fixture above.
- Residual risk: none beyond the standard fixture/screenshot gap — the version-scope correction (the one thing earlier project work got wrong on this topic) has already been applied throughout this article.
- Human Approval: not requested this round.
- Independent QA: not yet submitted to ChatGPT this round (Pilot A–D each went through this step; recommend the same for Pilot E before considering it fully confirmed, consistent with the pattern established this session).

## 9. Final Verdict

**DRAFT — TECHNICALLY SOUND PER EXISTING RECORDS AND OFFICIAL DOCS, NOT YET EVIDENCE-COMPLETE.**

Rationale: the article's central reproduced claim (the array formula's exact output against the documented test dataset) is a direct restatement of a project-verified reproduction already recorded in the decision log (Pilot E, PASS, no re-verification needed per the lightweight model). The version-scope claim — the one place earlier work on this topic was initially wrong — is corrected throughout and backed by official Microsoft documentation. The individual building-block functions are backed by official docs; the combined technique is honestly described as a well-known but not officially-documented-as-such pattern. No new research or Excel reproduction was performed this round. The article is **not** yet CONTENT READY, because — like Pilot A/B/C/D — no fixture or screenshots exist yet (§5). This completes Pilot A–E's initial conversion to production drafts; recommend independent ChatGPT QA before considering any of them past "content approved, screenshots pending."
