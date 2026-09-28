# QA / Publish-Readiness Package — "excel-trim-not-removing-nonbreaking-space"

Source article: `content/excel-trim-not-removing-nonbreaking-space.md`
Predecessor: Pilot C (`TRIM vs CHAR(160)`, Simple Task grade, but actual human-intervention cost was much higher than typical Simple Task — see decision log "생산성 / 사람 개입 정도" table) — no `content/pilot_C_*.md` file exists in this repo; the only prior record is `claude/비즈니스_방향_결정_로그.md` (2026-09-15 "Pilot C/D/E 실측 결과 및 Gate 판단" section) and `docs/pilot_results.md`'s summary row.
Prepared: 2026-09-22
Prepared by: Cowork (assistant), per `docs/content_operations_playbook.md`, using **only facts already recorded in the decision log — no new research, no new Excel reproduction this round** (per standing user instruction for Pilot A–E conversions). Official Microsoft doc URLs were looked up this round for citation purposes only (source-citation verification, consistent with how Pilot A/B handled this — not new investigation into behavior).
Revised: 2026-09-22, same day, per ChatGPT independent QA (see §9).
Status at end of this package: see "Final Verdict" at the bottom.

---

## 1. Article Metadata (for WordPress, NOT uploaded)

| Field | Value |
|---|---|
| Title | Why TRIM Isn't Removing Non-Breaking Spaces in Excel |
| Slug | `excel-trim-not-removing-nonbreaking-space` |
| Meta description | TRIM in Excel only removes regular spaces, not non-breaking spaces (U+00A0). Here's how to detect and remove them — and a CHAR(160) bug to watch for. (154 chars) |
| Category | Text Cleanup |
| Search Intent | Troubleshooting / Fix |
| QA grade (per `docs/qa_policy.md`) | Simple Task — **note:** decision log records that Pilot C's actual verification cost (6 screenshot round-trips, multiple diagnostic formulas to isolate the `CHAR(160)` behavior) was much higher than typical for this grade; this is flagged as a known exception, not a reason to reclassify the grade itself |
| Focus keyword (Rank Math) | excel trim not removing space |
| Version scope | All current Excel versions (formula-based, not a version-gated feature). The `CHAR(160)` behavior is confirmed on one configuration (Excel 2021, Korean-language Windows) and not generalized further |
| Internal link candidates | `excel-remove-blank-rows-guide` (Pilot G, production draft exists, not yet published); `power-query-remove-duplicates` (Pilot A, production draft exists, not yet published) — **neither linked in-body**, since neither is a live published URL yet |

## 2. Claim-by-Claim Evidence Map (no new research or reproduction performed this round)

| # | Claim in article | Evidence source | Status |
|---|---|---|---|
| 1 | `TRIM` removes leading/trailing regular spaces and collapses multiple regular spaces between words, but does not remove non-breaking space (code 160) | [TRIM function](https://support.microsoft.com/en-us/excel/functions/trim-function) — Microsoft Support, states this explicitly (per the wording already confirmed and quoted in the decision log's Pilot F ChatGPT-review-revision entry) | **Official doc, directly on point** — this is the strongest possible source, stronger than a project reproduction alone |
| 2 | `CLEAN` removes ASCII control characters (codes 0–31) and does not affect code 160 | [CLEAN function](https://support.microsoft.com/en-us/excel/functions/clean-function) — Microsoft Support | Official doc |
| 3 | `UNICHAR(n)` returns the character for Unicode code point `n`, independent of ANSI codepage | [UNICHAR function](https://support.microsoft.com/en-us/excel/functions/unichar-function) — Microsoft Support | Official doc |
| 4 | On the reproduced system (Excel 2021, Korean-language Windows), `CHAR(160)` returns a regular space (code 32) instead of the true non-breaking space, while `UNICHAR(160)` correctly returns code 160 | Decision log, Pilot C `[Observed]` — diagnosed via `UNICODE(MID(...))` character inspection and `=UNICODE(CHAR(160))` / `=UNICODE(UNICHAR(160))` direct tests | **Project-verified reproduction on one configuration** — root cause independently diagnosed, not inferred, and explicitly not generalized beyond that one configuration (revised per ChatGPT QA, see §9) |
| 5 | The `CHAR(160)`-based fix formula fails silently (no error, just doesn't fix the text) rather than erroring out | Same decision log entry — the SUBSTITUTE had "nothing matching to replace" because CHAR(160) wasn't returning code 160 | Project-verified reproduction |
| 6 | Whether this is a locale/codepage-dependent issue affecting other non-Western Windows locales is explicitly stated as untested | Article now says this has not been tested on other locales/versions, rather than asserting a mechanism or scope | **Revised to remove overgeneralization** (see §9) — the article previously speculated this "can potentially affect other non-Western Windows locales" and called it "not a one-time fluke tied to one machine"; both statements have been removed |

**Conclusion:** every claim in the article traces either to an official Microsoft doc (claims 1–3) or to this project's own diagnosed reproduction of the `CHAR(160)` behavior on one specific configuration (claims 4–5). Claim 6 has been rewritten to state plainly that broader applicability is untested, rather than asserting a codepage mechanism as the explanation (that mechanism is now offered only as "a plausible mechanism," not a settled cause).

## 3. Technical QA Checklist

| # | Item | Result |
|---|---|---|
| 1 | Every formula in the article is syntactically valid and matches documented function behavior | PASS |
| 2 | Every claimed behavior matches either official Microsoft documentation or project-recorded verification | PASS — this article is unusually well-grounded: its single most important claim (TRIM doesn't remove NBSP) is directly stated in Microsoft's own TRIM doc, not just inferred |
| 3 | Retained reproduction evidence (fixture and/or screenshot) exists | **FAIL / NOT YET MET** — no fixture file for this topic exists in this repo, and no screenshots exist. Same primary blocker pattern as Pilot A/B. |
| 4 | Version applicability statement is accurate | PASS — reframed this round to state the `CHAR(160)` finding is confirmed on one configuration only, with no claim about how far it generalizes |
| 5 | No known Blog B content trap is present, and this article's own trap (`CHAR(160)` vs `UNICHAR(160)`) is stated correctly and without overgeneralization | PASS — revised this round to remove the "not a one-time fluke," "can potentially affect other non-Western Windows locales," and "legacy behavior difference... that can affect any Windows installation" language flagged by ChatGPT's independent QA |

## 4. Fixture and Screenshot Requirements (NOT YET CAPTURED — primary blocker)

No fixture exists in this repo for this topic under `fixtures/`. Planned fixture (for a future round): one workbook with at least two cases — (a) a cell with a true non-breaking space (U+00A0) padding the text, and (b) a cell with a non-breaking space between two words — plus a column showing the `CHAR(160)` vs `UNICHAR(160)` codepage difference directly (e.g., `=UNICODE(CHAR(160))` and `=UNICODE(UNICHAR(160))` as visible formulas), captured on the same locale where the original behavior was found if possible, since it has only been confirmed on that one configuration.

| # | Scenario | Screenshot content needed | Alt text (draft) |
|---|---|---|---|
| 1 | NBSP padding a cell, TRIM alone fails | Formula bar with `=TRIM(A2)`, result still showing extra space / LEN mismatch | "TRIM formula failing to remove a non-breaking space in Excel" |
| 2 | Character-code diagnosis | `=UNICODE(MID(A2,1,1))` returning 160 | "UNICODE formula confirming a non-breaking space at code 160" |
| 3 | The `CHAR(160)` behavior on this configuration | `=UNICODE(CHAR(160))` returning 32 instead of 160 (on the tested Korean-language Windows configuration) | "CHAR(160) returning an unexpected character code on the tested Windows configuration" |
| 4 | The working fix | `=UNICODE(UNICHAR(160))` returning 160, and the full fix formula producing the correct trimmed result | "UNICHAR(160) correctly returning the non-breaking space on the tested configuration" |
| 5 | Before/after full fix formula | `=TRIM(SUBSTITUTE(CLEAN(A2),UNICHAR(160)," "))` result matching expected clean text and LEN | "Full fix formula removing non-breaking spaces and matching expected text length" |

**Status: fixture created (2026-09-28)** — `fixtures/excel-trim-not-removing-nonbreaking-space_fixture.xlsx`. Sheet `NBSP_Fix` has two rows, each with a real non-breaking space (U+00A0) embedded programmatically (not retyped), plus all formulas from the table above (`TRIM`, `UNICODE(MID(...))`, `UNICODE(CHAR(160))`, `UNICODE(UNICHAR(160))`, the failing `CHAR(160)`-based fix, and the working `UNICHAR(160)`-based fix), verified to compute correctly (LibreOffice headless recalculation: TRIM leaves the NBSP untouched, the UNICHAR-based fix correctly produces the clean text and length). A `Capture_Notes` sheet in the same file gives cell-by-cell instructions for the 5 screenshots below. **Still blocking:** English-UI screenshots have not yet been captured — same primary blocker as before, now reduced to a capture-only step. Screenshot 3 in particular must be captured on the same Korean-language-Windows regional settings where the original `CHAR(160)` behavior was found; if this machine's result differs (e.g. returns 160 instead of 32), that should be recorded plainly rather than assumed.

## 5. SEO/Search-Intent QA Checklist

| # | Item | Result |
|---|---|---|
| 1 | Focus keyword appears naturally in title, meta description, and body | PASS |
| 2 | Title matches search intent (Troubleshooting/Fix) and states the concrete symptom without overclaiming scope ("all spaces" → "non-breaking spaces", per ChatGPT QA) | PASS (revised this round) |
| 3 | Meta description is under ~160 characters | PASS (154 chars) |
| 4 | Headings (H2s) map onto distinct, scannable sub-tasks (why it fails, the fix, the CHAR(160) behavior, how to verify) | PASS |
| 5 | No keyword-density padding | PASS |
| 6 | Internal links only point to pages that actually exist | PASS — none inserted this round |

## 6. US English QA Checklist

| # | Item | Result |
|---|---|---|
| 1 | US spelling/vocabulary conventions throughout | PASS |
| 2 | Instructions use standard Excel formula/menu terminology | PASS |
| 3 | Grammar, punctuation, and formula/code-block formatting are correct and consistent | PASS |
| 4 | Tone matches Blog B's plain, task-focused style | PASS |
| 5 | Scope of the `CHAR(160)` claim is worded carefully (no "affects any Windows installation" or "not a one-time fluke" language) | PASS — revised this round per ChatGPT QA |

## 7. Publish-Readiness Status

- WordPress upload: **NOT performed** — Draft-only, per instruction (public publish requires separate user approval).
- Repo storage: revised article and this QA package to be committed to the repo this round; `docs/content_status.md` updated in the same commit.
- Fixture: **created (2026-09-28)** — `fixtures/excel-trim-not-removing-nonbreaking-space_fixture.xlsx`, verified via LibreOffice headless recalculation (see §4/§11).
- Screenshot evidence: **still not captured** — only remaining blocker (§4/§11); cell-by-cell capture plan is embedded in the fixture's `Capture_Notes` sheet.
- Residual risk: the `CHAR(160)` behavior has been confirmed on exactly one configuration (Excel 2021, Korean-language Windows); the article no longer speculates about other locales or claims a settled causal mechanism.
- Human Approval: not requested this round.
- Independent QA: submitted to ChatGPT for Technical/SEO/US-English review this round — verdict "revision required," changes applied, see §9.

## 8. Final Verdict

**DRAFT — CONTENT APPROVED, FIXTURE CREATED, PENDING ENGLISH-UI SCREENSHOTS ONLY.** (Per ChatGPT's second-round QA: "Pilot C: DRAFT — 내용 승인 가능, fixture·영문 UI 스크린샷 대기.")

Rationale: this article's central technical claim (TRIM doesn't remove non-breaking spaces) is stated directly in Microsoft's own official TRIM documentation. The `CHAR(160)` behavior is a project-verified, root-cause-diagnosed reproduction on one configuration, stated without overgeneralizing to "other non-Western locales" and without asserting an unverified causal mechanism (round 2 removed the "plausible mechanism" speculation per ChatGPT's second-round QA — see §10). No new research or Excel reproduction was performed this round. Content is approved; the sole remaining blocker before this can move past Draft is fixture creation and English-UI screenshot capture (§4).

## 9. Revision Round — ChatGPT Independent QA (2026-09-22)

**Verdict received:** 수정 필요 (revision required).

**Issue raised:** the article generalized a single reproduction (Excel 2021, Korean-language Windows) into claims about "other non-Western locales" and stated it was "not a one-time fluke tied to one machine" — overstating what was actually tested.

**Changes made:**
1. Removed the sentence claiming the issue "can potentially affect other non-Western Windows locales as well" and the sentence framing it as "not a one-time fluke tied to one machine."
2. Rewrote the locale-scope language to state plainly: this project reproduced the `CHAR(160)` behavior specifically on Excel 2021 / Korean-language Windows, and has not tested or generalized it to other locales, versions, or regional settings.
3. Reframed the ANSI-codepage explanation as "a plausible mechanism" rather than an established, generalizable cause.
4. Changed the section heading from "The Locale Bug: Use UNICHAR(160), Not CHAR(160)" to "A Formula That Can Fail: CHAR(160) vs. UNICHAR(160)" to avoid pre-labeling it a general "locale bug" in a heading before the scope caveat appears.
5. Changed the article title from "Why TRIM Isn't Removing All Spaces in Excel (Non-Breaking Space Fix)" to "Why TRIM Isn't Removing Non-Breaking Spaces in Excel" — the old title's "All Spaces" framing overclaimed scope (the article covers one specific space character, not all spaces).
6. Updated meta description to match the revised framing ("a CHAR(160) bug to watch for" instead of implying a general locale bug).
7. Updated the one-line summary and Sources section to match the revised, scope-limited framing throughout.

**Not changed:** the underlying technical facts (TRIM doesn't remove NBSP; CHAR(160) returned 32 instead of 160 on the tested machine; UNICHAR(160) returned 160 correctly) — these were not disputed by the QA and remain as originally recorded from the decision log.


## 10. Revision Round 2 — ChatGPT Independent QA (2026-09-23)

**Verdict received:** 방향은 맞지만 아직 최종 PASS는 아님 (direction correct, not yet final PASS) — one remaining issue.

**Issue raised:** the sentence "`UNICHAR` addresses a Unicode code point directly, rather than going through the legacy ANSI character-code mapping that `CHAR` uses — which is a plausible mechanism for why the two functions could diverge on a non-English Windows installation" was an unverified causal claim (a "plausible mechanism" is speculation, not a verified fact) and should be removed in favor of stating only what was actually measured.

**Change made:** replaced that sentence with: "On the tested machine, `UNICODE(UNICHAR(160))` returned 160 while `UNICODE(CHAR(160))` returned 32. That is why this article uses `UNICHAR(160)` for the NBSP replacement." — this states only the measured result and the practical conclusion drawn from it, with no claim about *why* the two functions diverge.

**Result:** ChatGPT's round-2 verdict for this article: **"Pilot C: DRAFT — 내용 승인 가능, fixture·영문 UI 스크린샷 대기"** (content approved, pending fixture/English-UI screenshots). This round's change has not yet been separately re-confirmed by ChatGPT (it was specified as the exact required fix), but per the reviewer's own stated condition, applying it moves this article past the "revision required" state to "content approved, screenshots pending."

## 11. Fixture Creation (2026-09-28)

Built `fixtures/excel-trim-not-removing-nonbreaking-space_fixture.xlsx` (sheet `NBSP_Fix`) with two rows: (a) a non-breaking space padding both ends of "Wireless Mouse", (b) a non-breaking space between "Wireless" and "Mouse" — both NBSP characters inserted programmatically via Python (`\u00A0`), not typed in Excel, to guarantee the correct character is present.

Formulas per the §4 requirements table: `LEN`, `TRIM`, `UNICODE(MID(...,1,1))`, `UNICODE(CHAR(160))`, `UNICODE(UNICHAR(160))`, the `CHAR(160)`-based fix formula, the `UNICHAR(160)`-based fix formula, and an expected-clean-text reference column with its own `LEN`.

**Verification note:** `UNICODE` and `UNICHAR` are post-2007 Excel functions; when written by a non-Excel tool (openpyxl) they must be stored in the underlying XML with an `_xlfn.` prefix (`_xlfn.UNICODE`, `_xlfn.UNICHAR`) or the file shows `#NAME?` for those cells when opened — this was caught during verification (first build attempt showed `#NAME?` under LibreOffice headless recalculation) and fixed before finalizing the fixture. Excel itself hides this prefix in the formula bar once the file is opened and saved normally.

Verified via `soffice --headless --convert-to xlsx` recalculation (Linux/LibreOffice, not the target Windows/Excel environment, used only to confirm formula validity and logic — not to reproduce the locale-specific `CHAR(160)` result): `TRIM` left the non-breaking space untouched in both rows (confirms the article's core claim), `UNICODE(MID(...))` correctly returned 160, `UNICODE(UNICHAR(160))` returned 160, and the `UNICHAR(160)`-based fix formula correctly produced "Wireless Mouse" (length 14) in both rows. `UNICODE(CHAR(160))` returned a value specific to this Linux/LibreOffice environment (not 32, and not meaningful for the article's Windows-specific claim) — this column's real value must come from the user's own Korean-language-Windows Excel, not from this cross-platform sanity check.

A `Capture_Notes` sheet in the same workbook gives the exact cell references, expected formula-bar contents, and draft alt text for each of the 5 required screenshots (same content as the §4 table above), so the capture step doesn't require re-deriving cell coordinates.

**Remaining blocker:** English-UI screenshot capture in Excel, on the machine where the original `CHAR(160)` behavior was found (Korean-language Windows regional settings), per the `Capture_Notes` sheet.

## 12. Screenshot Capture Confirmed (2026-09-28)

User captured all 5 required screenshots directly in Excel on the target machine (Korean-language Windows regional settings, English display language), using `fixtures/excel-trim-not-removing-nonbreaking-space_fixture.xlsx`. Saved to `evidence/excel-trim-not-removing-nonbreaking-space/`:

| # | File | Cell / formula shown | Measured result |
|---|---|---|---|
| 1 | `01-trim-fails-on-nbsp.png` | D2, `=TRIM(B2)` | Text unchanged (16 chars in, 16 chars out) — TRIM does not remove the non-breaking space |
| 2 | `02-unicode-mid-returns-160.png` | F2, `=UNICODE(MID(B2,1,1))` | 160 — confirms the leading character is a true non-breaking space |
| 3 | `03-unicode-char160-returns-32.png` | G2, `=UNICODE(CHAR(160))` | **32** — confirms the `CHAR(160)` bug reproduces on this machine too (matches the original decision-log finding on Korean-language Windows; this is a second, independent confirmation, not an assumption) |
| 4 | `04-unicode-unichar160-returns-160.png` | H2, `=UNICODE(UNICHAR(160))` | 160 — `UNICHAR(160)` returns the correct code point where `CHAR(160)` does not |
| 5 | `05-fix-formula-result.png` | K2:L2, `=TRIM(SUBSTITUTE(CLEAN(B2),UNICHAR(160)," "))` | "Wireless Mouse", length 14 — matches the expected clean text exactly |

**Technical QA item 3 (reproduction evidence) status: now PASS.** All 5 screenshots match the article's claims exactly, including the locale-specific `CHAR(160)` → 32 result, which is now confirmed on two separate occasions (original decision-log reproduction, and this fixture). No blockers remain except the standing Human Approval / WordPress upload step.

**Final Verdict updated:** DRAFT — CONTENT APPROVED, FIXTURE + SCREENSHOTS COMPLETE. Ready for WordPress Draft creation, pending user go-ahead (same protocol as Pilot G).

## 13. WordPress Draft Created (2026-09-28)

Created via REST API through the already-authenticated Claude Browser session (cookie + nonce, no credentials entered), same method as Pilot G:

- **Post ID 34**, slug `excel-trim-not-removing-nonbreaking-space`, status `draft`.
- Category: created new category "Text Cleanup" (id 4) via REST — did not exist yet on this site (only "Data Cleanup" and "Uncategorized" existed before).
- Content: full article converted to Gutenberg blocks matching `content/excel-trim-not-removing-nonbreaking-space.md` exactly, with 5 bolded `[IMAGE N — filename.png]` placeholder paragraphs marking insertion points (each also naming the suggested alt text), placed at the points in the article where each screenshot is most relevant:
  1. `01-trim-fails-on-nbsp.png` — after "Why TRIM Alone Isn't Enough"
  2. `05-fix-formula-result.png` — after "The Standard Fix Formula"
  3. `03-unicode-char160-returns-32.png` — in "A Formula That Can Fail"
  4. `04-unicode-unichar160-returns-160.png` — immediately after #3
  5. `02-unicode-mid-returns-160.png` — in "How to Check Whether This Affects You"
- Excerpt set to the meta description.
- Rank Math SEO fields set via `wp.data.dispatch('rank-math')` (REST does not expose Rank Math postmeta on this site, same finding as Pilot G): focus keyword `excel trim not removing space`, SEO title matching the article title, meta description matching the excerpt. Saved via `core/editor` `savePost()`, verified persisted after a full page reload.
- Post status confirmed `draft` before and after the SEO save.

**Remaining steps (same protocol as Pilot G):** user attaches the 5 images directly in the already-open editor (automated upload paths previously ruled out as inefficient/blocked); Cowork then sets alt text on each image (media library + inline `<img>`) using the exact wording from §4/§12; status stays Draft until a separate explicit publish approval.
