# Drive an agent to keep fixing code until tests go green

A goal condition written as checkable clauses keeps a headless agent working across turns until `npm test` exits 0, with `--max-turns` as the only thing that guarantees the loop ends. You break `slugify` on purpose in the [goal-demo/](goal-demo/) starter, read the shared `goal-condition.txt` and the Bash and PowerShell scripts that feed it in, then run the loop. You end holding a bounded autonomous run whose result, turn count and cost come back as fields in the JSON envelope.

------

## Setup

Start Claude Code in the starter and confirm the tests pass before introducing a deliberate failure:

```bash
cd demos/05-cli/05-always-on/goal-demo
npm install
npm test
```

Both tests pass: `slugify('Hello World')` and `slugify('--hello--')`.

## Part A: Introduce a Failing Edge Case

Ask Claude to introduce a bug that breaks one test:

```text
Modify src/slugify.ts so that slugify('--hello--') returns '--hello--' instead of 'hello'.
Do not update the test file.
```

Run the tests to confirm the failure:

```bash
npm test
```

The suite now reports 1 failed, 1 passed and exits with code 1.

## Part B: Inspect the Goal-Driven Agent

The success condition lives in [goal-demo/goal-condition.txt](goal-demo/goal-condition.txt) so the prompt and the condition stay separate:

```text
All of the following must hold:
- src/slugify.ts handles leading and trailing hyphens correctly (slugify('--hello--') === 'hello')
- npm test exits 0 with no skipped tests
- No file outside src/ was modified
Stop after 15 turns if the condition is not yet met.
```

[goal-demo/goal-demo.sh](goal-demo/goal-demo.sh) reads that file, hands it to a headless run, and parses the JSON envelope:

```bash
# --max-turns bounds the loop, --output-format json makes the run machine readable
# < /dev/null keeps claude from waiting on stdin, jq keeps the three fields worth showing
claude -p "Keep working until this goal is met.

$GOAL" \
  --allowed-tools "Read,Edit,Bash(npm:*)" \
  --permission-mode acceptEdits \
  --max-turns 15 \
  --output-format json < /dev/null | jq '{result: .result, turns: .num_turns, cost: .total_cost_usd}'
```

[goal-demo/goal-demo.ps1](goal-demo/goal-demo.ps1) is the same run in PowerShell:

```powershell
# --max-turns bounds the loop, --output-format json makes the run machine readable
# the backtick is PowerShell's line continuation
claude -p "Keep working until this goal is met.

$Goal" `
    --allowed-tools "Read,Edit,Bash(npm:*)" `
    --permission-mode acceptEdits `
    --max-turns 15 `
    --output-format json |
    # this pipeline is the PowerShell equivalent of the jq filter in the Bash twin
    ConvertFrom-Json |
    Select-Object @{ Name = 'result'; Expression = { $_.result } },
                  @{ Name = 'turns'; Expression = { $_.num_turns } },
                  @{ Name = 'cost'; Expression = { $_.total_cost_usd } } |
    ConvertTo-Json
```

## Part C: Observe the Loop

Run the script from the starter folder and watch the output:

```bash
bash goal-demo.sh
```

PowerShell:

```powershell
./goal-demo.ps1
```

A good outcome shows the agent making one or two edits to `slugify.ts`, running the tests, confirming they pass, and reporting the fix in the `result` field with a turn count well under the ceiling:

```json
{
  "result": "Goal met on turn 1. Added .replace(/^-+|-+$/g, '') to strip leading and trailing hyphens.",
  "turns": 6,
  "cost": 0.517722
}
```

If the agent hits the turn limit instead, check that the goal condition matches the exact function signature used in the test file.

The completed, runnable version of this demo lives in [goal-demo-solution/](goal-demo-solution/).
