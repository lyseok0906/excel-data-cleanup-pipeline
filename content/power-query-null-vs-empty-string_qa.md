# QA / Publish-Readiness Package — "power-query-null-vs-empty-string"

Source article: `content/power-query-null-vs-empty-string.md`
Predecessor: Pilot D (`Power Query null vs ""`, Edge-case Guide grade) — no `content/pilot_D_*.md` file exists in this repo; the only prior record is `claude/비즈니스_방향_결정_로그.md` (2026-09-15 "Pilot C/D/E 실측 결과 및 Gate 판단" section) and `docs/pilot_results.md`'s summary row.
Prepared: 2026-09-22
Prepared by: Cowork (assistant), per `docs/content_operations_playbook.md`, using **only facts already recorded in the decision log — no new research, no new Power Query reproduction this round** (per standing user instruction for Pilot A–E conversions). One official Microsoft doc URL (`Text.Combine`) was looked up this round for citation purposes only.
Revised: 2026-09-22, same day, per ChatGPT independent QA (see §9).
Status at end of this package: see "Final Verdict" at the bottom.

---

## 1. Article Metadata (for WordPress, NOT uploaded)

| Field | Value |
|---|---|
| Title | Power Query: Why null and "" (Empty String) Are Not the Same Thing |
| Slug | `power-query-null-vs-empty-string` |
| Meta description | In Power Query, null and an empty string look similar but behave differently — especially with Text.Combine. Here's the difference and how to avoid the bug. (155 chars) |
| Category | Power Query |
| Search Intent | Troubleshooting / Fix (Edge-case Guide) |
| QA grade (per `docs/qa_policy.md`) | Edge-case Guide |
| Focus keyword (Rank Math) | power query null vs empty string |
| Version scope | Power Query / Get & Transform, all current Excel versions and Power BI (M language behavior, not version-gated) |
| Internal link candidates | `power-query-remove-duplicates` (Pilot A, production draft exists, not yet published); `excel-remove-blank-rows-guide` (Pilot G, production draft exists, not yet published) — **neither linked in-body**, since neither is a live published URL yet |

## 2. Claim-by-Claim Evidence Map (no new research or reproduction performed this round)

| # | Claim in article | Evidence source | Status |
|---|---|---|---|
| 1 | `Text.Combine({[First],[Middle],[Last]}," ")` with `Middle = null` produces `"John Smith"` (one space) | Decision log, Pilot D `[Observed]` — direct single-execution reproduction in the Power Query advanced editor | Project-verified reproduction |
| 2 | Same formula with `Middle = ""` produces `"Jane  Doe"` (two spaces) | Same decision log entry | Project-verified reproduction |
| 3 | `null` values display in italics in the Power Query editor; `""` displays as a plain blank | Decision log, Pilot D `[Observed]` — "Middle 열도 null은 이탤릭체로, ""는 빈 칸으로 시각적으로 구분되어 표시됨" | Project-verified reproduction |
| 4 | General purpose/syntax of `Text.Combine` (joins a list of text values with a separator) | [Text.Combine](https://learn.microsoft.com/en-us/powerquery-m/text-combine) — Microsoft Learn | Official doc |
| 5 | The Go To Special > Blanks parallel is a related-but-not-identical distinction, not an identical mechanism | Article text revised this round to explicitly caveat that Excel's blank cell and Power Query's `null` are not the same data type and aren't run through the same code (see §9) | Framed as an analogy/reminder, not a technical equivalence claim — revised per ChatGPT QA |
| 6 | `Table.AddColumn(Source, "IsNull", each [Middle] = null, type logical)` / `Table.AddColumn(Source, "IsEmptyString", each [Middle] = "", type logical)` are runnable, standalone M steps | Standard, documented `Table.AddColumn` syntax (general M syntax, matches the exact snippet ChatGPT's QA specified) | Standard M syntax, corrected this round to be independently runnable (see §9) |
| 7 | `Table.ReplaceValue(Source, "", null, Replacer.ReplaceValue, {"Middle"})` normalizes `""` to `null` | Standard, documented `Table.ReplaceValue` syntax | Standard M syntax — not separately re-executed this round, low risk since it follows the documented function signature exactly |

**Conclusion:** the article's two central data points (the exact output for the null vs. "" cases) are direct restatements of a project-verified reproduction recorded in the decision log. The general `Text.Combine` syntax is backed by the official Microsoft Learn reference page. The Go To Special analogy is now explicitly scoped as an analogy rather than a claim of shared mechanism, and the diagnostic M snippet is now independently runnable rather than bare relational-operator syntax.

## 3. Technical QA Checklist

| # | Item | Result |
|---|---|---|
| 1 | Every M code snippet in the article is syntactically valid **and independently runnable as written** | PASS (revised this round — the previous `= [Middle] = null` / `= [Middle] = ""` lines were not standalone-runnable M without row context; replaced with `Table.AddColumn` steps, see §9) |
| 2 | Every claimed behavior matches either official Microsoft documentation or project-recorded verification | PASS |
| 3 | Retained reproduction evidence (fixture and/or screenshot) exists | **FAIL / NOT YET MET** — no fixture file for this topic exists in this repo, and no screenshots exist. Same primary blocker pattern as Pilot A/B/C. |
| 4 | Version applicability statement is accurate | PASS — Power Query/M behavior, not version-gated; correctly scoped to "all current Excel versions and Power BI" |
| 5 | No known Blog B content trap is present, and any cross-references to related traps (Go To Special > Blanks) are scoped as analogies, not asserted as the same mechanism | PASS — revised this round per ChatGPT QA (see §9) |

## 4. Fixture and Screenshot Requirements (NOT YET CAPTURED — primary blocker)

No fixture exists in this repo for this topic. Planned fixture (for a future round): a small table with a First/Middle/Last name structure, including at least one row with `Middle = null` and one row with `Middle = ""` (a genuine zero-length string, not a typed space) — **using the same First/Last values across both rows**, so any character-count comparison in a future revision is a fair like-for-like comparison rather than comparing two different names (this project's earlier draft compared "John Smith" against "Jane Doe," which ChatGPT's QA correctly flagged as weak evidence — see §9).

| # | Scenario | Screenshot content needed | Alt text (draft) |
|---|---|---|---|
| 1 | null vs "" visual distinction in the editor | Data preview showing italic null next to plain blank "" in the same column | "Power Query data preview showing null displayed in italics versus an empty string" |
| 2 | Text.Combine result with null | Result column showing single-space combined name for the null row | "Text.Combine skipping a null value and producing a single space between names" |
| 3 | Text.Combine result with "" | Result column showing double-space combined name for the empty-string row (same First/Last as the null row, for a fair comparison) | "Text.Combine not skipping an empty string, producing an extra space between names" |
| 4 | IsNull / IsEmptyString flag columns | `Table.AddColumn` result showing TRUE/FALSE flags correctly distinguishing the two rows | "Table.AddColumn flag columns distinguishing null from empty string row by row" |
| 5 | Fix applied | Table.ReplaceValue step converting "" to null, followed by consistent Text.Combine output for both rows | "Table.ReplaceValue normalizing empty strings to null before combining text" |

**Status: blocking**, same as Pilot A/B/C. English-UI capture required from the start.

## 5. SEO/Search-Intent QA Checklist

| # | Item | Result |
|---|---|---|
| 1 | Focus keyword appears naturally in title, meta description, and body | PASS |
| 2 | Title matches search intent (Troubleshooting/Fix, Edge-case Guide) and states the concrete distinction | PASS |
| 3 | Meta description is under ~160 characters | PASS (155 chars) |
| 4 | Headings (H2s) map onto distinct, scannable sub-tasks (the problem, why, how to tell apart, the fix) | PASS |
| 5 | No keyword-density padding | PASS |
| 6 | Internal links only point to pages that actually exist | PASS — none inserted this round |

## 6. US English QA Checklist

| # | Item | Result |
|---|---|---|
| 1 | US spelling/vocabulary conventions throughout | PASS |
| 2 | Instructions use standard Power Query terminology and M syntax | PASS |
| 3 | Grammar, punctuation, and code-block formatting are correct and consistent | PASS |
| 4 | Tone matches Blog B's plain, task-focused style | PASS |
| 5 | Cross-feature comparisons (Go To Special) are hedged appropriately rather than stated as equivalence | PASS — revised this round |

## 7. Publish-Readiness Status

- WordPress upload: **NOT performed** — Draft-only, per instruction (public publish requires separate user approval).
- Repo storage: revised article and this QA package to be committed to the repo this round; `docs/content_status.md` updated in the same commit.
- Fixture: **does not exist yet** — primary blocker (§4). Future fixture should use matching First/Last values across the null and "" rows, per §4.
- Screenshot evidence: **does not exist yet** — primary blocker (§4), depends on the fixture above.
- Human Approval: not requested this round.
- Independent QA: submitted to ChatGPT for Technical/SEO/US-English review this round — verdict "revision required," changes applied, see §9.

## 8. Final Verdict

**DRAFT — CONTENT APPROVED, PENDING FIXTURE / ENGLISH-UI SCREENSHOTS.** (Per ChatGPT's second-round QA: "Pilot D: DRAFT — 내용 승인 가능, fixture·영문 UI 스크린샷 대기.")

Rationale: the article's two central claims (the exact null-vs-"" output difference in `Text.Combine`) are direct restatements of a project-verified single-execution reproduction already recorded in the decision log (Pilot D, PASS with no re-verification needed per the lightweight model). The general `Text.Combine` syntax is backed by an official Microsoft Learn page. Round 2 fixed a preview-description contradiction in the opening paragraph, corrected the `Table.AddColumn` example to be a properly chained, independently runnable Advanced Editor sequence (with a separate Custom Column UI instruction), and confirmed code fences are clean 3-backtick pairs throughout (see §10). No new research or Power Query reproduction was performed this round. Content is approved; the sole remaining blocker before this can move past Draft is fixture creation and English-UI screenshot capture (§4).

## 9. Revision Round — ChatGPT Independent QA (2026-09-22)

**Verdict received:** 수정 필요 (revision required).

**Issues raised:**
1. The M code example (`= [Middle] = null` / `= [Middle] = ""`) was written as bare relational expressions without row/table context — not something a reader could paste in and run as a standalone step.
2. The Go To Special > Blanks paragraph asserted "the identical reason" as if it were literally the same mechanism as `Text.Combine`'s null-handling, which overstates the connection.
3. The `Text.Length` comparison between `"John Smith"` (10 chars) and `"Jane  Doe"` (9 chars) compared two different names, which is not valid evidence of the space-count difference — different names have different lengths regardless of the null/"" issue.

**Changes made:**
1. Replaced the non-runnable relational-expression example with the exact standalone `Table.AddColumn` snippet specified by the QA:
   ```
   Table.AddColumn(Source, "IsNull", each [Middle] = null, type logical)
   Table.AddColumn(Source, "IsEmptyString", each [Middle] = "", type logical)
   ```
   and added a sentence explaining these are steps that can be pasted into the Advanced Editor or built via Add Column > Custom Column.
2. Rewrote the Go To Special > Blanks paragraph to explicitly state that Excel's blank cell and Power Query's `null` "are not literally the same data type" and that Go To Special's selection logic "isn't run through the same code as `Text.Combine`" — reframed as a useful analogy/reminder rather than a claim of shared mechanism.
3. Removed the `Text.Length` numeric comparison between different names entirely. Added a note in §4 (Fixture Requirements) that a future fixture should use matching First/Last values across the null and "" rows, so any future length comparison is a fair like-for-like test.
4. Updated the one-line summary to reflect the corrected diagnostic approach (`Table.AddColumn` instead of bare relational checks) and removed the length-comparison framing.

**Not changed:** the underlying technical facts (Text.Combine skips null but not "", producing the documented one-space vs. two-space difference; the visual italic/non-italic distinction in the editor) — these were not disputed by the QA and remain as originally recorded from the decision log.


## 10. Revision Round 2 — ChatGPT Independent QA (2026-09-23)

**Verdict received:** 방향은 맞지만 아직 최종 PASS는 아님 (direction correct, not yet final PASS) — three remaining issues.

**Issues raised:**
1. The opening paragraph said `null` and `""` "look identical in the data preview," which contradicts the later statement that `null` displays in italics and `""` displays as a plain blank — an internal contradiction.
2. The `Table.AddColumn` example was written as two independent statements, not a properly chained Advanced Editor step sequence, and cannot be pasted as-is into the Custom Column dialog (which only accepts the expression after `each`, not the full `Table.AddColumn(...)` wrapper).
3. The reviewer's copy of the Markdown showed 4-backtick code fences in places (e.g., an `excel` fence opened with 3 backticks but apparently closed with 4) and asked for confirmation that the actual repo file uses clean 3-backtick fences throughout.

**Changes made:**
1. Rewrote the opening paragraph to: "A column that appears empty at a glance in Power Query can hold either `null` or `""` (an empty string). In this project's observed preview, `null` appeared in italics while an empty string appeared as a plain blank cell." This removes the "look identical" claim and states the actual observed visual difference immediately, consistent with the later "How to Tell Them Apart" section.
2. Replaced the `Table.AddColumn` example with a properly chained sequence (`IsNull = Table.AddColumn(Source, ...)`, `IsEmptyString = Table.AddColumn(IsNull, ...)` — the second step references the first by name, as a real Advanced Editor `let` block would), and added a separate paragraph clarifying that the Custom Column dialog only takes the expression after `each` (`[Middle] = null` / `[Middle] = ""`), not the full `Table.AddColumn(...)` wrapper.
3. Verified directly against the repo file (`grep -n` for triple-backtick fence lines) that all three code blocks in the article use clean, correctly paired 3-backtick fences with no stray 4-backtick sequences. The 4-backtick appearance in the material shared for review was an artifact of how that copy nested a ```markdown wrapper fence around code that itself contained ```excel fences when pasted into chat — not a defect in the actual repo file. No change was needed in the repo file itself for this point; confirmed clean.

**Result:** ChatGPT's round-2 verdict for this article: **"Pilot D: DRAFT — 내용 승인 가능, fixture·영문 UI 스크린샷 대기"** (content approved, pending fixture/English-UI screenshots), conditional on applying fixes 1 and 2 above (both applied) and confirming fix 3 (confirmed — no repo file change needed).

**Not changed:** the underlying technical facts (Text.Combine skips null but not "", producing the documented one-space vs. two-space difference; the visual italic/non-italic distinction in the editor) — these were not disputed by the QA and remain as originally recorded from the decision log.
