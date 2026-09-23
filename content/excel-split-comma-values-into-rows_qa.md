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
| 7 | Power Query's split-into-rows step has no single built-in "ignore empty" toggle (a separate filter step is needed) | Not directly stated in the official page cited; inferred from the documented step sequence, not from a project reproduction | **Disclosed as the weakest claim in the article (see Finding F below) — flagged, not re-verified this round** |

**Finding F (flag, not fabricated as verified):** claim #7 above is the one statement in this article that is neither an official-doc quote nor a project-reproduced result — it's a reasonable inference from how the Power Query UI is documented to work, carried over unchanged from this project's prior design notes (2026-09-10 LIVE TEST spec listed "blanks" as one of the four T1 validation dimensions, implying this was already a known consideration, but the decision log does not record a specific reproduced outcome for it). The article's own wording softens this ("does not have a single... toggle" rather than an absolute claim) and offers a workaround rather than asserting a specific mechanism. This should be the first thing re-verified when fixture/screenshot work happens for this article.

**Conclusion:** 6 of 7 claims trace directly to either an official Microsoft page or a project-reproduced result already in the decision log. One claim (#7) is disclosed as unverified inference rather than presented as confirmed fact — consistent with the "no overstated/unconfirmed claims" rule.

## 3. Technical QA Checklist

| # | Item | Result |
|---|---|---|
| 1 | Every formula/UI-step sequence in the article is accurate to current Excel/Power Query behavior as documented | PASS (see claim map above; item 7 flagged, not failed — it's disclosed rather than overstated) |
| 2 | Every claimed behavior matches either official Microsoft documentation or project-recorded verification | PASS with Finding F disclosed |
| 3 | Retained reproduction evidence (fixture and/or screenshot) exists for each method | **FAIL / NOT YET MET** — no fixture file for this topic exists in this repo, and no screenshots exist. Same primary blocker pattern as Pilot A. |
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

**Status: blocking**, same as Pilot A. English-UI capture required from the start.

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
- Repo storage: article and this QA package committed to the repo this round; `docs/content_status.md` updated in the same commit.
- Fixture: **does not exist yet** — primary blocker (§4).
- Screenshot evidence: **does not exist yet** — primary blocker (§4), depends on the fixture above.
- Residual risk: Finding F (claim #7, Power Query's blank-handling behavior) is the one claim to re-verify first when fixture/screenshot work begins for this article.
- Human Approval: not requested this round.

## 8. Final Verdict

**DRAFT — CONTENT APPROVED (per ChatGPT independent QA, 2026-09-23) — PENDING FIXTURE / ENGLISH-UI SCREENSHOTS.**

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
