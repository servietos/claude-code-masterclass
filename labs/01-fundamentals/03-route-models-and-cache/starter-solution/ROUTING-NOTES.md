# Routing notes

| Task | Model | Input | Output | Cache write | Cache read | Context used | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | haiku | 4 | 1917 | 32009 | 66656 | 51.5k / 1m (5%) | pass: diff touches exactly the three named files |
| A | sonnet | 6 | 1315 | 34171 | 115388 | 52.6k / 1m (5%) | pass: diff touches exactly the three named files |
| A | opus | 6 | 1439 | 35411 | 112346 | 51.5k / 1m (5%) | pass: diff touches exactly the three named files |
| B | haiku | 6 | 1668 | 34260 | 117918 | 53.6k / 1m (5%) | pass: names billable_kg, // truncation, proposes rounding up |
| B | sonnet | 4 | 567 | 32348 | 65015 | 50.9k / 1m (5%) | pass: names billable_kg, floor division, proposes rounding up |
| B | opus | 4 | 522 | 32492 | 64142 | 50.5k / 1m (5%) | pass: names billable_kg, floor division, proposes rounding up |
| C | haiku | 4 | 4441 | 33533 | 66564 | 53.8k / 1m (5%) | pass: distinct structures, files named, rejections justified |
