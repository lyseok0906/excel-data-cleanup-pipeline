# QA / Publish-Readiness Package — "power-query-null-vs-empty-string"

Source article: `content/power-query-null-vs-empty-string.md`
Predecessor: Pilot D (`Power Query null vs ""`, Edge-case Guide grade) — no `content/pilot_D_*.md` file exists in this repo; the only prior record is `claude/비즈니스_방향_결정_로그.md` (2026-09-15 "Pilot C/D/E 실측 결과 및 Gate 판단" section) and `docs/pilot_results.md`'s summary row.
Prepared: 2026-09-22
Prepared by: Cowork (assistant), per `docs/content_operations_playbook.md`, using **only facts already recorded in the decision log — no new research, no new Power Query reproduction this round** (per standing user instruction for Pilot A–E conversions). One official Microsoft doc URL (`Text.Combine`) was looked up this round for citation purposes only.

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
| 1 | `Text.Combine({[First],[Middle],[Last]}," ")` with `Middle = null` produces `"John Smith"` (10 chars) | Decision log, Pilot D `[Observed]` — direct single-execution reproduction in the Power Query advanced editor | Project-verified reproduction |
| 2 | Same formula with `Middle = ""` produces `"Jane  Doe"` (9 chars, two spaces) | Same decision log entry | Project-verified reproduction |
| 3 | `null` values display in italics in the Power Query editor; `""` displays as a plain blank | Decision log, Pilot D `[Observed]` — "Middle 열도 null은 이탤릭체로, ""는 빈 칸으로 시각적으로 구분되어 표시됨" | Project-verified reproduction |
| 4 | General purpose/syntax of `Text.Combine` (joins a list of text values with a separator) | [Text.Combine](https://learn.microsoft.com/en-us/powerquery-m/text-combine) — Microsoft Learn | Official doc |
| 5 | The parallel to Excel's Go To Special > Blanks (selects genuine blanks, not `""` results) | This project's own separately-documented finding (Pilot G / decision log's "알려진 콘텐츠 함정" #3), already established as a confirmed project fact, cross-referenced here rather than re-derived | Project-verified (cross-reference to an already-established fact, not new research) |
| 6 | `Table.ReplaceValue(Source, "", null, Replacer.ReplaceValue, {"Middle"})` normalizes `""` to `null` | Standard, documented `Table.ReplaceValue` syntax (function signature is general M syntax, not specific to this project's reproduction) | Standard M syntax — not separately verified by project reproduction this round, but not a claim about a special/surprising behavior either, just the mechanical application of a well-documented function |

**Conclusion:** the article's two central data points (the exact output strings and lengths for the null vs. "" cases) are direct restatements of a project-verified reproduction recorded in the decision log. The general `Text.Combine` syntax is backed by the official Microsoft Learn reference page. The one claim not separately re-verified this round is the `Table.ReplaceValue` fix syntax, which is standard, well-documented M function usage rather than a claim about surprising behavior — flagged here for transparency (Finding G) rather than silently treated as equivalent in evidentiary weight to the reproduced claims.

**Finding G (flag, not a blocker):** the `Table.ReplaceValue` fix snippet was not independently re-executed this round. It follows the function's standard documented signature exactly, so the risk of it being wrong is low, but it has not been run against a fixture to confirm the resulting `Text.Combine` output. This should be the first thing checked when fixture/screenshot work happens for this article.

## 3. Technical QA Checklist

| # | Item | Result |
|---|---|---|
| 1 | Every M code snippet in the article is syntactically valid | PASS |
| 2 | Every claimed behavior matches either official Microsoft documentation or project-recorded verification | PASS, with Finding G disclosed for the one non-reproduced snippet (the fix) |
| 3 | Retained reproduction evidence (fixture and/or screenshot) exists | **FAIL / NOT YET MET** — no fixture file for this topic exists in this repo, and no screenshots exist. Same primary blocker pattern as Pilot A/B/C. |
| 4 | Version applicability statement is accurate | PASS — Power Query/M behavior, not version-gated; correctly scoped to "all current Excel versions and Power BI" |
| 5 | No known Blog B content trap is present, and this article correctly cross-references the related Go To Special > Blanks trap rather than contradicting it | PASS — the cross-reference to the Go To Special trap is consistent with how that trap is described elsewhere in the decision log |

## 4. Fixture and Screenshot Requirements (NOT YET CAPTURED — primary blocker)

No fixture exists in this repo for this topic. Planned fixture (for a future round): a small table with a First/Middle/Last name structure, including at least one row with `Middle = null` and one row with `Middle = ""` (a genuine zero-length string, not a typed space), plus a `Text.Combine` step and a `Text.Length` check column.

| # | Scenario | Screenshot content needed | Alt text (draft) |
|---|---|---|---|
| 1 | null vs "" visual distinction in the editor | Data preview showing italic null next to plain blank "" in the same column | "Power Query data preview showing null displayed in italics versus an empty string" |
| 2 | Text.Combine result with null | Result column showing single-space combined name for the null row | "Text.Combine skipping a null value and producing a single space between names" |
| 3 | Text.Combine result with "" | Result column showing double-space combined name for the empty-string row | "Text.Combine not skipping an empty string, producing an extra space between names" |
| 4 | Length check | Text.Length column showing the numeric difference between the two rows | "Text.Length confirming the character count difference caused by an empty string" |
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

## 7. Publish-Readiness Status

- WordPress upload: **NOT performed** — Draft-only, per instruction (public publish requires separate user approval).
- Repo storage: article and this QA package to be committed to the repo this round; `docs/content_status.md` updated in the same commit.
- Fixture: **does not exist yet** — primary blocker (§4).
- Screenshot evidence: **does not exist yet** — primary blocker (§4), depends on the fixture above.
- Residual risk: Finding G (the `Table.ReplaceValue` fix snippet) should be the first thing re-verified when fixture/screenshot work begins for this article.
- Human Approval: not requested this round.

## 8. Final Verdict

**DRAFT — TECHNICALLY SOUND PER EXISTING RECORDS AND OFFICIAL DOCS, NOT YET EVIDENCE-COMPLETE.**

Rationale: the article's two central claims (the exact null-vs-"" output difference in `Text.Combine`) are direct restatements of a project-verified single-execution reproduction already recorded in the decision log (Pilot D, PASS with no re-verification needed per the lightweight model). The general `Text.Combine` syntax is backed by an official Microsoft Learn page. One supporting snippet (the `Table.ReplaceValue` fix) is standard documented M syntax but was not independently re-executed this round — disclosed as Finding G rather than glossed over. No new research or Power Query reproduction was performed this round. The article is **not** yet CONTENT READY, because — like Pilot A/B/C — no fixture or screenshots exist yet (§4). Next in sequence: Pilot E.
