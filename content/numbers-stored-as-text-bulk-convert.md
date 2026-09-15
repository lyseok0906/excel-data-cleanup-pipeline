---
title: "How to Convert Numbers Stored as Text in Excel (4 Bulk Methods)"
slug: "numbers-stored-as-text-bulk-convert"
meta_description: "Fix numbers stored as text in Excel with 4 reliable bulk methods: Convert to Number, Paste Special Multiply, VALUE(), and Text to Columns — plus the hidden non-breaking-space case."
category: "Data Cleanup"
focus_keyword: "numbers stored as text excel"
internal_link_candidates:
  - "excel-remove-blank-rows-guide" # working slug for the Pilot G blank-rows article, once it is converted to production (NOT published yet — do not create or link until that article itself is production-ready)
  - "excel-textsplit-vs-power-query" # candidate future article referenced only as a topical link idea, not yet written
status: "DRAFT — NOT UPLOADED TO WORDPRESS — PENDING HUMAN APPROVAL"
---

# How to Convert Numbers Stored as Text in Excel (4 Bulk Methods)

If a column of numbers is left-aligned, shows a small green triangle in the corner of each cell, or calculations such as `SUM` ignore the values, Excel may be treating those values as text rather than numbers. This is common after importing data from CSV files, databases, or copy-pasting from a website.

Here are four ways to fix it in bulk, plus a hidden-character case that can make a value look like it's still text after you've tried one of them.

**Applies to:** Excel for Microsoft 365, Excel 2024, Excel 2021, Excel 2019, and Excel 2016. All four methods below use only long-standing Excel features (no new dynamic-array functions), so they work the same way across every version in this list.

## Method 1: Error Checking Button (fastest when available)

If Excel's background error checking is on, cells with text-stored numbers can show a small green triangle in the top-left corner.

1. Select the cells you want to convert.
2. Click the warning icon that appears next to the selection.
3. Choose **Convert to Number**.

If you do not see the warning icon, background error checking may be disabled under **File > Options > Formulas > Enable background error checking**.

## Method 2: Paste Special → Multiply

This method works even when the error-checking indicator is unavailable:

1. Type `1` in an empty cell.
2. Copy that cell.
3. Select the range containing numbers stored as text.
4. Open **Paste Special**.
5. Choose **Multiply** under **Operation**, then click **OK**.

Multiplying by 1 forces text-formatted numeric values to become numeric values while leaving their displayed numbers unchanged.

## Method 3: VALUE() Helper Column

For mixed or messy imports, a helper column makes the conversion visible and easier to audit:

1. In a new column, enter `=VALUE(A2)` and adjust the reference as needed.
2. Fill the formula down.
3. Copy the converted results.
4. Use **Paste Special > Values** if you want to replace the original text values.
5. Remove the helper column when finished.

`VALUE` converts text that Excel recognizes as a valid number, date, or time into a numeric value.

## Method 4: Text to Columns

Text to Columns can also cause Excel to reinterpret simple numeric text using the **General** column format.

1. Select the column containing the text-stored numbers.
2. Go to **Data > Text to Columns**.
3. Keep the column format as **General**.
4. Finish the wizard.

Use this method carefully if the source contains leading zeros, long identifiers, dates, or mixed text-and-number values, because automatic conversion may change how those values are represented.

## If Conversion Still Fails, Check for Hidden Characters

A value can look numeric while still containing a hidden character, such as a non-breaking space (NBSP, Unicode character 160) left over from a web copy-paste or an export from another system. When a value contains one, the methods above may not convert it, because Excel still sees a text string rather than a clean number.

`TRIM` removes ordinary spaces (the character you get from pressing the spacebar, code 32) and collapses multiple spaces between words down to one — but by itself it does not remove the non-breaking space character. `CLEAN` removes the first 32 nonprinting ASCII control characters (codes 0–31); the non-breaking space falls outside that range, so `CLEAN` does not address it either. In other words, `TRIM` and `CLEAN` are each scoped to a different kind of unwanted character, and neither is designed to target a literal U+00A0.

To target the non-breaking space specifically, use `UNICHAR(160)`, which returns the Unicode character for code point 160 — the non-breaking space — so it can be matched and replaced explicitly:

```excel
=VALUE(TRIM(SUBSTITUTE(CLEAN(A2),UNICHAR(160)," ")))
```

This formula uses `CLEAN` to strip ordinary control characters, `SUBSTITUTE` with `UNICHAR(160)` to swap the literal non-breaking space for a regular space, `TRIM` to clean up the result, and `VALUE` to convert the cleaned text into a number.

## Which Version of Excel Do You Need?

All five techniques in this article — the four bulk-conversion methods and the `UNICHAR` fix — work in Microsoft 365, Excel 2024, Excel 2021, Excel 2019, and Excel 2016. None of them depend on newer dynamic-array functions like `UNIQUE`, `FILTER`, or `TEXTSPLIT`, so there is no version-specific fallback needed here.

## One-line Summary

For a quick one-time fix, use **Convert to Number** or **Paste Special > Multiply**. For mixed imported data, use a helper formula such as `VALUE()` so you can see which rows converted successfully before replacing the source values. If a value still won't convert, check for a hidden non-breaking space and use the `UNICHAR(160)` formula above.

## Sources

- [Convert numbers stored as text to numbers in Excel](https://support.microsoft.com/en-us/office/convert-numbers-stored-as-text-to-numbers-in-excel-40105f2a-fe79-4477-a171-c5bad0f0a885) — Microsoft Support. Backs Method 1 (error-checking indicator, Convert to Number) and Method 3 (`VALUE` as a helper-column method).
- [Fix text-formatted numbers by applying a number format](https://support.microsoft.com/en-us/office/fix-text-formatted-numbers-by-applying-a-number-format-6599c03a-954d-4d83-b78a-23af2c8845d0) — Microsoft Support. Backs Method 2 (Paste Special with Multiply).
- [VALUE function](https://support.microsoft.com/en-us/office/value-function-257d0108-07dc-437d-ae1c-bc2d3953d8c2) — Microsoft Support. Reference for the `VALUE` function used in Method 3 and in the hidden-character formula.
- [TRIM function](https://support.microsoft.com/en-us/office/trim-function-410388fa-c5df-49c6-b16c-9e5630b479f9) — Microsoft Support. Explicitly documents the non-breaking space (decimal 160) and states that TRIM alone does not remove it — the basis for the "Check for Hidden Characters" section.
- [CLEAN function](https://support.microsoft.com/en-us/excel/functions/clean-function) — Microsoft Support. Documents that CLEAN removes only the first 32 nonprinting ASCII control characters, which do not include the non-breaking space.
- [UNICHAR function](https://support.microsoft.com/en-us/office/unichar-function-ffeb64f5-f131-44c6-b332-5cd72f0659b8) — Microsoft Support. Reference for `UNICHAR`, which returns the Unicode character for a given code point (160 for the non-breaking space).
- [Split text into different columns with the Convert Text to Columns Wizard](https://support.microsoft.com/en-us/office/split-text-into-different-columns-with-the-convert-text-to-columns-wizard-30b14928-5550-41f5-97ca-7a3e9c363ed7) — Microsoft Support. General reference for the Text to Columns wizard used in Method 4. **Note:** this page does not document the specific behavior of "General" format reinterpreting text-stored numbers — that claim rests on this project's own reproduction in Excel (recorded separately in the project's QA package), not on this official page.
