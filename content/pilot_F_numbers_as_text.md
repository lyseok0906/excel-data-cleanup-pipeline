# How to Convert Numbers Stored as Text to Real Numbers in Excel (Bulk Fix)

If a column of numbers is left-aligned, shows a small green triangle in the corner of each cell, or calculations such as `SUM` ignore the values, Excel may be treating those values as text rather than numbers. This is common after importing data from CSV files, databases, or copy-pasting from a website.

Here are four ways to fix it in bulk.

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

A value can look numeric while still containing spaces or imported nonprinting characters.

For ordinary leading/trailing spaces and low ASCII control characters, `TRIM` and `CLEAN` can help. A non-breaking space is different: `CLEAN` does not reliably remove it, and `TRIM` is designed around ordinary spaces.

For the non-breaking-space case tested in this Blog B project, use `UNICHAR(160)` explicitly, for example:

```excel
=VALUE(TRIM(SUBSTITUTE(CLEAN(A2),UNICHAR(160)," ")))
```

The `UNICHAR(160)` form is preferred here because the project live test found that `CHAR(160)` can behave differently under some Windows locale/code-page combinations.

## One-line Summary

For a quick one-time fix, use **Convert to Number** or **Paste Special > Multiply**. For mixed imported data, use a helper formula such as `VALUE()` so you can see which rows converted successfully before replacing the source values.
