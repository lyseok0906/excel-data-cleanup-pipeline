---
title: "Split Comma-Separated Values into Rows in Excel (TEXTSPLIT vs Power Query)"
slug: "excel-split-comma-values-into-rows"
meta_description: "Split comma-separated values into their own rows in Excel. TEXTSPLIT works in Microsoft 365 and Excel 2024; older versions need the Power Query fallback."
category: "Power Query"
focus_keyword: "excel split comma separated values into rows"
internal_link_candidates:
  - "power-query-remove-duplicates" # Pilot A, production draft exists — not yet published, do not link until it exists
  - "excel-remove-blank-rows-guide" # Pilot G, production draft exists — not yet published, do not link until it exists
status: "DRAFT — NOT UPLOADED TO WORDPRESS — PENDING HUMAN APPROVAL — fixture and screenshots not yet captured"
---

# Split Comma-Separated Values into Rows in Excel (TEXTSPLIT vs Power Query)

A single cell like `Apple, Banana, Cherry` sometimes needs to become three separate rows instead of three separate columns — for example, to make each value filterable, sortable, or usable in a pivot table. Excel has two ways to do this, and which one you can use depends on your Excel version.

**Applies to:** Excel for Microsoft 365 and Excel 2024 (`TEXTSPLIT`, native row-splitting); Excel 2021, 2019, and 2016 (Power Query fallback — `TEXTSPLIT` is not available).

## Method 1: TEXTSPLIT (Microsoft 365 / Excel 2024 only)

`TEXTSPLIT` splits text using a delimiter you specify, and it can split into rows, not just columns, by passing the delimiter as the `row_delimiter` argument instead of the default `col_delimiter`:

```excel
=TEXTSPLIT(A2, , ",")
```

This splits the text in `A2` on commas and spills the results **downward into separate rows** starting at the formula's cell (the blank argument skips `col_delimiter` so only `row_delimiter` is used).

Microsoft documents three behaviors of `TEXTSPLIT` that matter for this task:

- **`row_delimiter`**: the argument that controls splitting into rows, as used above.
- **`ignore_empty`**: when set to `TRUE`, consecutive delimiters (for example, `Apple,,Cherry`) do not produce a blank row between values. The default is `FALSE`, which does produce blank entries for empty splits.
- **Multiple delimiters**: `row_delimiter` accepts an array of delimiters (for example, `{",", ";"}`), so a column mixing comma- and semicolon-separated values can be split with one formula.

Because the formula spills, do not type anything into the cells below it — `TEXTSPLIT` needs that space to place the split results, and existing content there will cause a `#SPILL!` error.

## Why TEXTSPLIT Might Not Work For You

`TEXTSPLIT` is a newer dynamic-array function. This project directly reproduced the following in Excel 2021: entering a `TEXTSPLIT` formula returns `#NAME?` — Excel 2021 does not recognize the function name at all, across every delimiter/blank/multiple-delimiter case tested. This matches Microsoft's own version scoping for the function, which lists Microsoft 365 and Excel 2024 as the supported versions.

If you see `#NAME?` after typing a `TEXTSPLIT` formula, that is very likely the cause — not a typo in the formula.

## Method 2: Power Query (Excel 2021, 2019, 2016)

Power Query's **Split Column by Delimiter**, using the **Rows** option instead of the default **Columns** option, does the same job on older Excel versions:

1. Select the column you want to split.
2. Go to **Data > Get & Transform > From Table/Range** (or open the query in Power Query Editor if the data is already a query).
3. Right-click the column, choose **Split Column > By Delimiter**.
4. Choose your delimiter (Comma, Semicolon, or Custom).
5. Under **Split into**, choose **Rows** instead of the default **Columns**.
6. Click **OK**, then **Close & Load**.

Unlike `TEXTSPLIT`'s `ignore_empty` argument, Power Query's split-into-rows step does not have a single toggle for skipping blank results — if you need to drop blank rows produced by consecutive delimiters, add a filter step afterward (for example, filter the split column to exclude blank/null values) rather than relying on the split step itself to skip them.

For multiple delimiters in the same column, use **Custom** and enter each delimiter, or run the split step twice (once per delimiter) if your data mixes delimiter types inconsistently.

## Which Method Should You Use?

| | TEXTSPLIT | Power Query |
|---|---|---|
| Excel version | Microsoft 365, Excel 2024 only | 2016, 2019, 2021, 2024, Microsoft 365 (all versions) |
| Result type | Formula (recalculates automatically when source cell changes) | Query (needs "Refresh" to pick up source changes) |
| Skips blank splits | Yes, via `ignore_empty` argument | Not directly — filter afterward |
| Multiple delimiters | Yes, via a delimiter array | Yes, via Custom delimiter entry or repeated split steps |

If you're on Microsoft 365 or Excel 2024, `TEXTSPLIT` is simpler for a one-off, self-updating formula. If you're on an older version, or you're already building a Power Query pipeline for other cleanup steps, the Power Query method keeps everything in one place and doesn't depend on a specific Excel version.

## One-line Summary

Use `TEXTSPLIT(cell, , delimiter)` to split values into rows on Microsoft 365 or Excel 2024. On Excel 2021, 2019, or 2016 — where `TEXTSPLIT` returns `#NAME?` — use Power Query's **Split Column > By Delimiter**, choosing **Rows** instead of **Columns**, and filter out blank results afterward since there's no built-in "ignore empty" toggle in that step.

## Sources

- [TEXTSPLIT function](https://support.microsoft.com/en-us/excel/functions/textsplit-function) — Microsoft Support. Backs the `row_delimiter`, `ignore_empty`, and multiple-delimiter-array behavior described in Method 1, and the Microsoft 365 / Excel 2024 version scoping.
- [Split a column of text (Power Query)](https://support.microsoft.com/en-us/office/split-a-column-of-text-power-query-5282d425-6dd0-46ca-95bf-8e0da9539662) — Microsoft Support. Backs the Split Column by Delimiter steps in Method 2, including the Rows-vs-Columns choice.
- The specific finding that `TEXTSPLIT` returns `#NAME?` in Excel 2021 (rather than simply being described as "unsupported") was independently reproduced by this project in real Excel 2021 across all tested delimiter/blank/multiple-delimiter cases, recorded in the Pilot A/B LIVE TEST section of the project decision log — not solely from the official page above. The claim that Power Query's split-into-rows step has no single "ignore empty" toggle (requiring a separate filter step) is based on the documented steps of the feature rather than a project reproduction; it has not been independently re-verified in Excel this round, consistent with this round's "no new research" instruction.
