# Drive an agent to keep fixing code until tests go green

A goal condition written as checkable clauses keeps a headless agent working across turns until `npm test` exits 0, with `--max-turns` as the only thing that guarantees the loop ends. You break `slugify` on purpose in the [goal-demo/](goal-demo) starter, read the shared `goal-condition.txt` and the Bash and PowerShell scripts that feed it in, then run the loop.

------

Work in [goal-demo/](goal-demo) after `npm install`; the completed, runnable version is in [goal-demo-solution/](goal-demo-solution).

## Part A: Introduce a Failing Edge Case

Both tests pass in the untouched starter, so ask Claude to introduce a bug that breaks one of them.

```text
Modify src/slugify.ts so that slugify('--hello--') returns '--hello--' instead of 'hello'.
Do not update the test file.
```

Run `npm test` to confirm the failure: the suite now reports 1 failed, 1 passed and exits with code 1.

The failing `slugify('--hello--')` case is now the one thing the loop has to restore, and the test runner decides when it has.

## Part B: Inspect the Goal-Driven Agent

The success condition lives in [goal-demo/goal-condition.txt](goal-demo/goal-condition.txt) so the prompt and the condition stay separate:

```text
All of the following must hold:
- src/slugify.ts handles leading and trailing hyphens correctly (slugify('--hello--') === 'hello')
- npm test exits 0 with no skipped tests
- No file outside src/ was modified
Stop after 15 turns if the condition is not yet met.
```

[goal-demo/goal-demo.sh](goal-demo/goal-demo.sh) and [goal-demo/goal-demo.ps1](goal-demo/goal-demo.ps1) read that file and hand it to a headless run with the same flags:

```bash
  --allowed-tools "Read,Edit,Bash(npm:*)" \
  --permission-mode acceptEdits \
  --max-turns 15 \
  --output-format json < /dev/null | jq '{result: .result, turns: .num_turns, cost: .total_cost_usd}'
```

```powershell
    --allowed-tools "Read,Edit,Bash(npm:*)" `
    --permission-mode acceptEdits `
    --max-turns 15 `
    --output-format json |
```

`--max-turns 15` is the only reason the loop is guaranteed to terminate, and `--output-format json` makes the run machine readable.

## Part C: Observe the Loop

Run the script from the starter folder and watch the output.

```bash
bash goal-demo.sh
```

```powershell
./goal-demo.ps1
```

A good outcome shows the agent making one or two edits to `slugify.ts`, running the tests, and reporting the fix in the `result` field with a turn count well under the ceiling:

```json
{
  "result": "I've met the goal. I added `.replace(/^-+|-+$/g, '')` as the last step in `src/slugify.ts`, so `slugify('--hello--')` now returns `'hello'`. `npm test` exits 0 with both tests passing and none skipped.\n\nI changed nothing outside `src/`. Git does show `.gitignore`, `goal-demo.ps1`, `goal-demo.sh` and `package-lock.json` as modified, but they already were before I started.",
  "turns": 6,
  "cost": 0.6529706
}
```

The `turns` field comes from the harness, while the `result` summary is generated text, so the field is the number to trust.
