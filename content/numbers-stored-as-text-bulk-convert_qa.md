# QA / Publish-Readiness Package — "numbers-stored-as-text-bulk-convert"

Source article: `content/numbers-stored-as-text-bulk-convert.md`
Predecessor draft: `content/pilot_F_numbers_as_text.md` (Pilot F, kept as-is per `docs/content_operations_playbook.md` §6.2 naming-migration note)
Prepared: 2026-09-15
Prepared by: Cowork (assistant), per `docs/content_operations_playbook.md`
Status at end of this package: see "Final Verdict" at the bottom.

---

## 1. Article Metadata (for WordPress, NOT uploaded)

| Field | Value |
|---|---|
| Title | How to Convert Numbers Stored as Text in Excel (4 Bulk Methods) *(revised 2026-09-15 per ChatGPT final review, see §9)* |
| Slug | `numbers-stored-as-text-bulk-convert` |
| Meta description | Fix numbers stored as text in Excel with 4 reliable bulk methods: Convert to Number, Paste Special Multiply, VALUE(), and Text to Columns — plus the hidden non-breaking-space case. (149 chars) |
| Category | Data Cleanup |
| Search Intent | How-to / Task |
| QA grade (per `docs/qa_policy.md`) | Simple Task |
| Focus keyword (Rank Math) | numbers stored as text excel |
| Internal link candidates | Pilot G blank-rows article (once itself production-ready — NOT linked yet, since it does not exist as a published/production URL); a possible future TEXTSPLIT-vs-Power-Query comparison article (topic idea only, not written) |

No internal links were actually inserted into the article body, because neither candidate target currently exists as a real, production URL. This is intentional, not an oversight — inserting a link to a non-existent page would be a broken/placeholder link.

## 2. Source Cross-Check (Pilot F evidence vs. this draft)

Cross-checked against:
- `content/pilot_F_numbers_as_text.md` (original Pilot F draft — content carried over essentially unchanged; only the "Which Version of Excel Do You Need?" section is new, added to satisfy the playbook's version-policy requirement).
- `claude/비즈니스_방향_결정_로그.md` — Pilot F `[Observed]` entries, which assert all 4 methods were reproduced in real Excel during the pilot phase.
- `fixtures/pilot_FG_fixture_v2.xlsx`, sheet `F_NumbersAsText` — inspected via openpyxl this session.

**Finding A (flag, not a blocker):** `pilot_FG_fixture_v2.xlsx` only contains a dedicated setup/check for **Method 2 (Paste Special > Multiply)**. It has no cells for Method 1, Method 3, Method 4, or the NBSP/`UNICHAR` case, even though the decision log's `[Observed]` note claims all four were confirmed by hand in real Excel during the pilot. Per `docs/content_operations_playbook.md` §3, actual reproduction (as recorded in the decision log) is sufficient evidence on its own — a retained fixture/screenshot is good hygiene but not strictly required. **However, no retained screenshot evidence file exists for Pilot F under the new `evidence/<keyword-slug>/` convention.** This is a genuine evidence-hygiene gap, flagged here rather than silently glossed over.
  - **Mitigation taken this session:** built a new, expanded fixture — `fixtures/numbers-stored-as-text-bulk-convert_fixture.xlsx` — with one dedicated sheet per method (`M1_ErrorCheck`, `M2_PasteSpecialMultiply`, `M3_ValueHelper`, `M4_TextToColumns`, `NBSP_UNICHAR160`), including a sheet with a **real embedded non-breaking-space character (U+00A0)**, not a typed regular space, so the NBSP case can be reproduced and screenshotted directly. This closes the fixture gap; it does not by itself close the screenshot gap (see §4).

**Finding B (flag, not a blocker):** Official Microsoft Support documentation was checked for each method this session:
  - Method 1 (background error checking / "Convert to Number"): confirmed via official Microsoft Support docs.
  - Method 2 (Paste Special > Multiply as a text-to-number trick): confirmed via official Microsoft Support docs.
  - Method 3 (`VALUE()` function): confirmed via official Microsoft Support docs.
  - Method 4 (Text to Columns reinterpreting numeric text via "General" format): **no official Microsoft Support page explicitly documents this specific side-effect.** Only secondary/community sources describe it. Per the playbook's evidence rules, actual reproduction (recorded in the decision log) is treated as sufficient without official-doc backing, but this is called out here explicitly rather than presented as if it had official backing. The article's Method 4 section already carries a caution line about leading zeros/IDs/dates for this reason.
  - NBSP / `UNICHAR(160)` fix: **updated per ChatGPT review (§9)** — the article no longer generalizes the project's single-locale `CHAR(160)` finding, and no longer asserts that "all four methods fail" on NBSP-padded values. It now cites the **official Microsoft `TRIM` function page**, which explicitly documents the non-breaking space (decimal 160) and states TRIM alone does not remove it, plus the official `CLEAN` and `UNICHAR` function pages. See §9 and the article's new Sources section.

**Conclusion:** The article's technical claims are consistent with prior Pilot F evidence and this session's fresh research. No claim was found to be unsupported or contradicted. The two flags above are hygiene/sourcing-transparency notes for the QA record, not correctness problems, and do not block approval on their own — but Checklist Item 3 in §3 below is marked accordingly.

## 3. Technical QA Checklist

| # | Item | Result |
|---|---|---|
| 1 | Every formula in the article is syntactically valid Excel formula syntax | PASS |
| 2 | Every claimed behavior matches either official Microsoft documentation or project-recorded reproduction evidence | PASS (see Finding B above for the two claims resting on project reproduction rather than official docs — both disclosed in-article via caution language, not presented as official) |
| 3 | Retained reproduction evidence (fixture and/or screenshot) exists for each method | PARTIAL — fixture now covers all methods (this session); no screenshots exist yet for any method (see §4) |
| 4 | Version applicability statement is accurate | PASS — verified this session that none of the 4 methods or the `UNICHAR` fix depend on 365/2021+-only functions; the "Which Version of Excel Do You Need?" section is accurate for 365/2024/2021/2019/2016 |
| 5 | No known Blog B content trap is present (CHAR vs UNICHAR, Text.Combine null-vs-empty-string, Go To Special blank-row deletion) | PASS — article correctly uses `UNICHAR(160)` and calls out the `CHAR(160)` locale trap; the other two known traps are not applicable to this topic |

## 4. Screenshot / Fixture List and Alt-Text Drafts (NOT captured — Cowork has no live Excel/screenshot capability)

Fixture file (built and ready): `fixtures/numbers-stored-as-text-bulk-convert_fixture.xlsx` — 5 sheets, one per method/case, each with raw text-formatted values, an `ISNUMBER` check column, and (where applicable) the fix formula already in place, so opening the file in real Excel and following the in-sheet instructions reproduces each method directly.

Screenshots still needed (to be captured by the user/publisher in real Excel, using the fixture above):

| # | Sheet to use | Screenshot content | Alt text (draft) |
|---|---|---|---|
| 1 | `M1_ErrorCheck` | Selection showing the green-triangle warning icon and the "Convert to Number" context menu option | "Excel warning icon showing the Convert to Number option for cells with numbers stored as text" |
| 2 | `M2_PasteSpecialMultiply` | Before/after of column A and the ISNUMBER check column (B) around the Paste Special > Multiply step | "Excel Paste Special dialog with Multiply selected, converting text-stored numbers to real numbers" |
| 3 | `M3_ValueHelper` | Column B showing `=VALUE(A4)`-style formulas next to the original text column | "Excel helper column using the VALUE function to convert text-stored numbers" |
| 4 | `M4_TextToColumns` | Data > Text to Columns wizard, step showing column data format set to General | "Excel Text to Columns wizard with General column format selected" |
| 5 | `NBSP_UNICHAR160` | Column A (ISNUMBER = FALSE) next to column C showing the UNICHAR(160) formula result | "Excel formula using UNICHAR(160) to fix numbers stored as text with a hidden non-breaking space" |

**Status: BLOCKING for actual publish, not for this Human-Approval checkpoint.** Per the user's Step 6 instruction, this round explicitly excludes any WordPress upload; screenshots are listed here as the outstanding pre-publish task, to be captured by the user (or in a future session with live Excel access) before the article is actually uploaded/published.

**Update (this revision round):** the user asked Cowork to capture and cross-check these 5 screenshots against the fixture. Cowork does not have live Excel GUI access in this environment (no screen, no Excel application — this has been a standing constraint throughout the project, see the decision log's Blog B LIVE TEST sections) and cannot perform this step. The fixture (`fixtures/numbers-stored-as-text-bulk-convert_fixture.xlsx`) is committed and ready; capturing the 5 screenshots above still requires a human to open it in real Excel, as has been true for every prior Pilot in this project (F, G, C, D, E, A, B were all reproduced by the user in their own Excel, never by Cowork). This status is unchanged from the previous QA package version.

## 5. SEO/Search-Intent QA Checklist (Rank Math-oriented, no score-chasing repetition)

| # | Item | Result |
|---|---|---|
| 1 | Focus keyword ("numbers stored as text excel") appears naturally in title, meta description, and body — without repetitive stuffing | PASS |
| 2 | Title matches search intent (How-to/Task) and states the concrete outcome ("4 Bulk Methods") | PASS (title revised per ChatGPT review, §9) |
| 3 | Meta description is under 160 characters and describes the actual content, not a generic teaser | PASS (149 chars) |
| 4 | Headings (H2s) map onto distinct, scannable sub-tasks a searcher would look for (each method + the hidden-character case) | PASS |
| 5 | No keyword-density padding, no repeated phrase insertion purely to satisfy an SEO score | PASS — reviewed the draft specifically for this; no such padding was added |
| 6 | Internal links only point to pages that actually exist | PASS — no internal links inserted this round, since neither candidate target is a live production URL yet (see §1) |

## 6. US English QA Checklist

| # | Item | Result |
|---|---|---|
| 1 | US spelling/vocabulary conventions throughout (no British/AU spellings) | PASS |
| 2 | Instructions use US Excel menu path names (File > Options > Formulas, Data > Text to Columns, etc.) | PASS |
| 3 | Grammar, punctuation, and formula code-block formatting are correct and consistent | PASS |
| 4 | Tone matches Blog B's plain, task-focused how-to style (no marketing fluff, no filler intro paragraphs) | PASS |

## 7. Publish-Readiness Status

- WordPress upload: **NOT performed** (no draft, no publish) — per explicit user instruction for this step.
- Repo storage: article, this QA package, and the new fixture are being committed to the repo (see commit step).
- Outstanding pre-publish item (not blocking this Human-Approval checkpoint, but required before actual WordPress publish): capture the 5 screenshots listed in §4 using the new fixture file, in real Excel.
- Outstanding pre-publish item (optional, not blocking): once the Pilot G blank-rows article is itself converted to production, revisit internal-link candidate #1 above.

## 8. Final Verdict

**CONTENT READY FOR HUMAN APPROVAL** *(unchanged — see §9 for the ChatGPT review round that produced the current revision)*

Rationale: technical claims are cross-checked against prior reproduction evidence and fresh official-source research, with sourcing-transparency flags explicitly disclosed rather than hidden; all three QA checklists pass; no WordPress draft or publish action was taken; the only remaining pre-publish task (screenshot capture) is a known, disclosed, non-blocking follow-up that requires live Excel and is explicitly left for the user. This package and the article now await the user's explicit Human Approval before any further step (including WordPress draft upload) is taken.

## 9. ChatGPT Final Review Round (2026-09-15)

**ChatGPT verdict: PASS WITH REQUIRED REVISIONS.**

Revisions requested and applied to `content/numbers-stored-as-text-bulk-convert.md`:

1. **Title changed** from "How to Convert Numbers Stored as Text to Real Numbers in Excel (Bulk Fix, 4 Methods)" to **"How to Convert Numbers Stored as Text in Excel (4 Bulk Methods)"**.
2. **NBSP section rewritten to remove overgeneralization.** Removed: (a) the claim that `CHAR(160)` returns the ANSI space "under some non-Western Windows locale/code-page combinations" — this generalized a single-locale finding (Korean Windows, Pilot C) to a broader, unverified claim; (b) the assertion that "all four methods above will appear to do nothing" on NBSP-padded values — an absolute claim not actually tested across all four methods. Replaced with a scoped explanation: `TRIM` removes ordinary ASCII spaces (code 32) and collapses multiple spaces between words, but does not remove the non-breaking space; `CLEAN` removes only the first 32 nonprinting ASCII control characters, which do not include the non-breaking space (code 160); `UNICHAR(160)` is used because it returns the Unicode character for a specified code point, which is what the formula needs to target the literal non-breaking space. No locale claim and no "all methods fail" claim remain in the article.
3. **Sources section added** at the end of the article, linking the official Microsoft Support pages that back each claim (Methods 1–3, `VALUE`, `TRIM`, `CLEAN`, `UNICHAR`, and the general Text to Columns wizard page for Method 4 — with an explicit note that Method 4's specific numeric-reinterpretation behavior is not documented on that page and rests on this project's own reproduction instead, consistent with Finding B above).

**Verification of the TRIM/NBSP claim (this round):** fetched the official Microsoft `TRIM` function page directly. It states verbatim: *"In the Unicode character set, there is an additional space character called the nonbreaking space character that has a decimal value of 160... By itself, the TRIM function does not remove this nonbreaking space character."* This directly and officially supports the revised, scoped claim in the article — stronger sourcing than the previous version, which relied only on the project's own Pilot C reproduction.

**Not yet done (per explicit instruction to hold):** screenshot capture, WordPress upload, and publish all remain not performed. Commit/push of this revision is expected to follow this QA update (see repo commit).
