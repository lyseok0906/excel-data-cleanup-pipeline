---
title: "Why TRIM Isn't Removing All Spaces in Excel (Non-Breaking Space Fix)"
slug: "excel-trim-not-removing-nonbreaking-space"
meta_description: "TRIM in Excel only removes regular spaces, not non-breaking spaces (U+00A0). Here's how to detect and remove them — and a locale bug to watch for."
category: "Text Cleanup"
focus_keyword: "excel trim not removing space"
internal_link_candidates:
  - "excel-remove-blank-rows-guide" # Pilot G, production draft exists — not yet published, do not link until it exists
  - "power-query-remove-duplicates" # Pilot A, production draft exists — not yet published, do not link until it exists
status: "DRAFT — NOT UPLOADED TO WORDPRESS — PENDING HUMAN APPROVAL — fixture and screenshots not yet captured"
---

# Why TRIM Isn't Removing All Spaces in Excel (Non-Breaking Space Fix)

If `=TRIM(A2)` still leaves extra space in a cell — or two values that look identical still fail an exact-match comparison — the cause is usually a **non-breaking space** (NBSP, Unicode character U+00A0, decimal code 160), not a regular space. TRIM does not remove it, and the usual fix formula can silently fail depending on your Windows language settings.

**Applies to:** all current Excel versions (Excel for Microsoft 365, Excel 2024, Excel 2021, Excel 2019, Excel 2016). The locale issue described below has been confirmed on Excel 2021 running on Korean-language Windows; it is a Windows-locale/codepage issue, not a version issue, so it can potentially affect other non-Western Windows locales as well — this has not been tested on every locale.

## Why TRIM Alone Isn't Enough

Microsoft's own documentation for the `TRIM` function states that the Unicode character set includes an additional space character with decimal value 160 — the non-breaking space commonly used on web pages — and that `TRIM` by itself does not remove this character. `TRIM` removes regular ASCII spaces (character code 32) from the start and end of text and collapses multiple spaces between words down to one, but it does not touch character code 160.

This matters because non-breaking spaces commonly end up in Excel data pasted from web pages, PDFs, or other applications that use them to prevent line breaks. The cell can look completely normal — same font, same visible spacing — while `LEN()` reports a longer string than expected, or an exact-match formula (`=A2=B2`) returns `FALSE` for text that appears identical.

`CLEAN` does not solve this either: `CLEAN` removes the first 32 ASCII control characters (character codes 0–31, non-printing characters like line breaks and tabs), not code 160. A non-breaking space is a printable character, not a control character, so `CLEAN` has no effect on it.

## The Standard Fix Formula

The general-purpose pattern for stripping both regular and non-breaking spaces is:

```excel
=TRIM(SUBSTITUTE(CLEAN(A2), UNICHAR(160), " "))
```

Read this from the inside out:
1. `CLEAN(A2)` strips any non-printing control characters.
2. `SUBSTITUTE(..., UNICHAR(160), " ")` replaces every non-breaking space with a regular space.
3. `TRIM(...)` then collapses the now-all-regular spaces and trims the ends.

## The Locale Bug: Use `UNICHAR(160)`, Not `CHAR(160)`

A common version of this formula uses `CHAR(160)` instead of `UNICHAR(160)`:

```excel
=TRIM(SUBSTITUTE(A2, CHAR(160), CHAR(32)))
```

This project directly reproduced a case where this formula **silently fails** to fix the problem — not with an error, but by leaving the non-breaking spaces in place, so the result still doesn't match the expected clean value.

The root cause, confirmed through direct diagnosis in Excel (checking the actual character codes in the source text with `UNICODE(MID(...))`, then testing `=UNICODE(CHAR(160))` directly): on the Windows configuration where this was reproduced (Excel 2021, Korean-language Windows), `CHAR(160)` did not return the Unicode non-breaking space at all — it returned a regular space (character code 32), based on the system's ANSI codepage rather than the Unicode code point. Because `CHAR(160)` was quietly returning the wrong character, `SUBSTITUTE` had nothing matching to replace, and the non-breaking spaces in the text were left untouched.

`UNICHAR(160)`, confirmed in the same diagnosis (`=UNICODE(UNICHAR(160))` returned 160 as expected), reliably returns the true Unicode non-breaking space regardless of the system's ANSI codepage, because `UNICHAR` addresses a Unicode code point directly rather than going through the legacy ANSI character-code mapping that `CHAR` uses. **`UNICHAR(160)` is the version that should be used in any formula that needs to target the non-breaking space specifically.**

This is not a one-time fluke tied to one machine — it is a legacy behavior difference between `CHAR` (ANSI codepage-dependent) and `UNICHAR` (Unicode-code-point-based) that can affect any Windows installation using a non-Western ANSI codepage. It has been confirmed on Korean-language Windows; if you're on a different non-English Windows locale and your `CHAR(160)`-based formula doesn't seem to be working, this locale/codepage difference is the first thing to check.

## How to Check Whether This Affects You

Before assuming a fix formula worked, verify it rather than trusting that it ran without an error:

1. Check the actual character code(s) around the suspect space with `=UNICODE(MID(A2, n, 1))` for the relevant position `n`. A non-breaking space returns 160; a regular space returns 32.
2. Check what your own `CHAR(160)` actually returns: `=UNICODE(CHAR(160))`. If this returns 160, `CHAR(160)` is working correctly as a non-breaking space on your system. If it returns 32 (or anything other than 160), use `UNICHAR(160)` instead in any formula that needs to target the non-breaking space.
3. After applying the fix formula, re-check the result's length with `LEN()` against the expected clean length, rather than assuming success because the formula didn't error.

## One-line Summary

`TRIM` alone does not remove non-breaking spaces (character code 160); use `=TRIM(SUBSTITUTE(CLEAN(A2), UNICHAR(160), " "))`. Prefer `UNICHAR(160)` over `CHAR(160)` — on some non-Western Windows locales, `CHAR(160)` silently returns a regular space instead of the true non-breaking space, which makes a `CHAR(160)`-based fix formula fail without any error message.

## Sources

- [TRIM function](https://support.microsoft.com/en-us/excel/functions/trim-function) — Microsoft Support. States that Unicode includes an additional space character (decimal value 160, the non-breaking space used on web pages) and that `TRIM` by itself does not remove it.
- [UNICHAR function](https://support.microsoft.com/en-us/excel/functions/unichar-function) — Microsoft Support. Backs `UNICHAR`'s behavior of returning the character for a given Unicode code point.
- [CLEAN function](https://support.microsoft.com/en-us/excel/functions/clean-function) — Microsoft Support. Backs the statement that `CLEAN` removes the first 32 ASCII control characters and does not affect character code 160.
- The specific locale bug — `CHAR(160)` returning a regular space (code 32) instead of the non-breaking space on Korean-language Windows, while `UNICHAR(160)` correctly returns code 160 — was independently diagnosed and confirmed by this project through direct reproduction in Excel (character-code inspection via `UNICODE(MID(...))` and `UNICODE(CHAR(160))`), recorded in the Pilot C entry of the project decision log. This is a project-verified reproduction, not solely a claim from official documentation, and it has been confirmed on one specific locale (Korean-language Windows) rather than tested exhaustively across all non-Western Windows locales.
