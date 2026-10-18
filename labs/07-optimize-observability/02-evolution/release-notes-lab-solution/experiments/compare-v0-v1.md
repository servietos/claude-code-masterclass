# Compare v0 to v1

Passes in the with-arm, three runs each, from `experiments/v0/aggregate-result.json` and
`experiments/v1/aggregate-result.json`.

| Grader | v0 | v1 | Direction | Delta |
|---|---|---|---|---|
| `version-heading` (target) | 0 of 3 | 3 of 3 | improved | +3 |
| `features-heading` (target) | 0 of 3 | 3 of 3 | improved | +3 |
| `fixes-heading` (target) | 1 of 3 | 3 of 3 | improved | +2 |
| `no-merge` | 3 of 3 | 3 of 3 | unchanged | 0 |
| `read-commits` | 3 of 3 | 3 of 3 | unchanged | 0 |
| `skill-fired` (indicator) | 3 of 3 | 3 of 3 | unchanged | 0 |
| runs with an error | 0 | 0 | unchanged | 0 |

Decision: PROMOTE. The target improved, nothing else regressed, and no run errored.
