# How to Remove Blank Rows in Excel Without Deleting Partially Blank Data

**Go To Special > Blanks > Delete Entire Row** is fast, but it selects blank *cells*, not rows that are completely empty. If your range contains partially completed records, that shortcut can delete valid rows. If one of the deleted rows is explicitly referenced by another formula, it can also produce a `#REF!` error.

This guide shows the risky shortcut and a safer way to delete only rows that are fully blank.

## The Standard Shortcut

1. Select only the data range you intend to clean.
2. Press **Ctrl+G**, click **Special**, choose **Blanks**, then click **OK**.
3. Excel selects every blank cell in that range.
4. If you then choose **Delete > Entire Row**, every row containing one of those selected blank cells can be deleted.

That last step is the trap.

## Why Partially Blank Rows Can Be Deleted

Suppose this customer data contains:

- a fully blank row,
- Bob with a missing phone number,
- Dave with a missing email address.

Bob and Dave are not blank records. They are incomplete records.

However, **Go To Special > Blanks** selects Bob's empty Phone cell and Dave's empty Email cell along with cells in the truly blank rows. If you then delete entire rows, Bob and Dave can be removed with the blank rows.

That is a data-loss problem even before formulas are considered.

## When #REF! Can Appear

Microsoft documents that `#REF!` occurs when a formula contains a reference that is no longer valid, commonly because referenced cells, rows, or columns were deleted.

This does **not** mean every row deletion breaks every formula. Excel can adjust many range references automatically.

The failure case is clearest when a formula explicitly references a row that you accidentally delete. In the live-test fixture, a formula explicitly references Bob's row. When the unsafe blank-cell workflow deletes Bob's partially blank row, the formula is expected to return `#REF!`.

If you notice the mistake immediately, **Ctrl+Z** is the safest recovery.

## Safer Method: Delete Only Fully Blank Rows

Use a helper column that counts non-empty cells in each record.

For a three-column dataset in A:C:

```excel
=COUNTA(A4:C4)
```

Fill the formula down.

Interpret the result as follows:

- `0` = the row is completely blank across the checked columns
- `1` or more = at least one field contains data, so the row should not be treated as fully blank

Then:

1. Filter the helper column to `0`.
2. Delete only the visible fully blank rows.
3. Clear the filter.
4. Remove the helper column if you no longer need it.

This protects partially complete records such as Bob and Dave.

## Formula Design Also Matters

Microsoft recommends using continuous ranges where appropriate instead of lists of explicit cell references.

For example:

```excel
=SUM(B2:D2)
```

is generally more resilient to structural changes than:

```excel
=SUM(B2,C2,D2)
```

because Excel can adjust a continuous range when rows or columns inside that range are removed.

That is a separate defense from the `COUNTA` helper. The helper prevents accidental record deletion; resilient formula design reduces the chance that structural edits create broken references.

## One-line Summary

**Go To Special > Blanks** selects blank cells, so deleting entire rows from that selection can remove valid partially blank records. If you only want rows that are completely empty, filter on a `COUNTA(...)=0` helper first.
