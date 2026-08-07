---
name: data-aggregator
description: Builds a dependency-free JavaScript module that groups records by a field, sums a numeric column, and prints a one-line-per-group report. Use when the user asks to "aggregate by field", "group sales by region", "revenue breakdown by dimension", "sum orders by product category", or "roll up records into totals".
---

# Data Aggregator

## Inputs

Before writing code, collect: the record field that groups the rows, the numeric field that gets summed, the target file name, and whether records may arrive with the numeric field missing.

## Workflow

1. Confirm the input schema: field names, types, and which fields are required.
2. Define the output contract: shape, sort order, and key type.
3. Implement the aggregation function.
4. Add a formatting function that produces a human-readable single-line-per-group report.
5. Embed a runnable sample dataset so the module can be verified with node directly.

## Constraints

- Use plain JavaScript with no external dependencies.
- Export named functions only.
- Keep business logic in the aggregation function, not the formatter.
- Place the runnable sample at the bottom of the output file, not in a separate test file, wrapped in an `if (require.main === module)` guard so importing the module prints nothing.

## Example

User says: "aggregate orders by product category and show me the revenue"

Actions: agree on `{ category, amount }` as the record shape, return `[{ category, total }]` sorted by `total` descending, write `ordersByCategory` plus `formatReport`, append 8 sample records, then run the file with node.

Result:

```text
Region: East  Revenue: $2450.00
Region: North  Revenue: $2146.00
Region: South  Revenue: $2031.00
```

## Troubleshooting

Error: `SyntaxError: Unexpected token 'export'` when running the file with node.
Cause: ESM syntax in a `.js` file that node resolves as CommonJS.
Solution: use `module.exports`, or rename the file to `.mjs`.

Error: totals come back as `NaN`.
Cause: the summed field is a string or missing on some records.
Solution: coerce with `Number(value) || 0` before adding.
