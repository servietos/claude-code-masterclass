---
presents: demo-always-on.md
budget: 4 min
beats: 4
---

# Present: Drive an agent to keep fixing code until tests go green

What separates a goal condition from a wish, and why an unattended loop ends at a turn ceiling whatever the model thinks of its own progress. Four beats: the condition as a specification, the assertion that makes it checkable, the three flags, and the envelope read against the prose.

------

**Shell:** beats 3 and 4 quote Bash; [`goal-demo.ps1`](goal-demo/goal-demo.ps1) carries the identical flag list, with `ConvertFrom-Json` standing in for `jq`. Say that in beat 3: the flags belong to `claude`, the parsing belongs to the shell. The `< /dev/null` is a POSIX redirect that PowerShell rejects, so the `.ps1` has none: the goal arrives as an argument.

## Beats

### Beat 1: a goal condition is a checkable claim, kept out of the script (1 min)

**Open:** [`goal-condition.txt`](goal-demo/goal-condition.txt) · [`src/slugify.ts`](goal-demo/src/slugify.ts)
**Say:** What separates a goal from a wish is whether running something answers it yes or no. "Fix the bug" leaves an unattended agent no way to know it is finished.

```text
All of the following must hold:
- src/slugify.ts handles leading and trailing hyphens correctly (slugify('--hello--') === 'hello')
- npm test exits 0 with no skipped tests
- No file outside src/ was modified
Stop after 15 turns if the condition is not yet met.
```

**Result:** four clauses, four yes-or-no answers: a named input with its expected output, an exit code, a blast radius, a ceiling

**Gotcha:** the condition lives in its own file, so what "done" means changes without touching the harness around it.

### Beat 2: the second clause is only checkable because this assertion exists (1 min)

**Open:** [`test/slugify.test.ts`](goal-demo/test/slugify.test.ts) · the `describe` block
**Say:** Every clause needs something in the repo capable of deciding it, or the agent grades it by opinion. Here the executing model is also the judge, tolerable only while judging is delegated to a command with an exit code.

```ts
describe('slugify', () => {
  it('converts text to slug', () => {
    expect(slugify('Hello World')).toBe('hello-world');
  });

  it('strips leading and trailing hyphens', () => {
    expect(slugify('--hello--')).toBe('hello');
  });
});
```

**Result:** both cases pass in the untouched starter, so clause two has something to decide it before Part A breaks anything

**Gotcha:** the goal condition and the second `it` are one statement written twice, once for the agent and once for the runner. Raise the stakes and you split the roles.

### Beat 3: three flags turn a prompt into a bounded autonomous loop (1 min)

**Open:** [`goal-demo.sh`](goal-demo/goal-demo.sh) · `GOAL=` through the `jq` projection
**Say:** Unattended means nobody answers a confirmation, so every stopping point is settled in advance. It also means nothing outside the run notices it going nowhere.

```bash
# the goal condition lives in its own file, so the prompt below stays one readable line
GOAL=$(cat "$(dirname "$0")/goal-condition.txt")

# --max-turns bounds the loop, --output-format json makes the run machine readable
# < /dev/null keeps claude from waiting on stdin, jq keeps the three fields worth showing
claude -p "Keep working until this goal is met.

$GOAL" \
  --allowed-tools "Read,Edit,Bash(npm:*)" \
  --permission-mode acceptEdits \
  --max-turns 15 \
  --output-format json < /dev/null | jq '{result: .result, turns: .num_turns, cost: .total_cost_usd}'
```

**Result:** the recorded run came back at 6 turns and $0.6529706, well inside the ceiling

**Gotcha:** `--max-turns 15` is the only reason the loop is guaranteed to terminate. Budget it as cost per turn times the ceiling.

### Beat 4: check the envelope's fields against the prose (1 min)

**Open:** [`readme.md`](readme.md#permission-modes-and-turn-controls) · [`goal-demo-solution/src/slugify.ts`](goal-demo-solution/src/slugify.ts), the line the loop restored
**Say:** An agent's closing summary is generated text like everything else it produced. The envelope around it is measured by the harness.

**Result:** a real recorded run. The prose says the goal was met and names no turn count; the measured `turns` is 6

```json
{
  "result": "I've met the goal. I added `.replace(/^-+|-+$/g, '')` as the last step in `src/slugify.ts`, so `slugify('--hello--')` now returns `'hello'`. `npm test` exits 0 with both tests passing and none skipped.\n\nI changed nothing outside `src/`. Git does show `.gitignore`, `goal-demo.ps1`, `goal-demo.sh` and `package-lock.json` as modified, but they already were before I started.",
  "turns": 6,
  "cost": 0.6529706
}
```

**Gotcha:** a run reporting 15 has almost certainly hit the limit without finishing, which usually means the goal condition and the test file disagree about the function under repair.

## If the room asks

| Question | Answer |
|---|---|
| Is `--max-turns` a soft target? | A hard cap. The run stops there whether or not the condition holds. |
| Why `acceptEdits` as well as `--allowed-tools`? | One pre-approves the tool set, the other covers the per-edit confirmation. Either one missing stalls the run. |
| Can the agent cheat by editing the test? | The third clause forbids it, and a deterministic evaluator reading `git status` can enforce that clause. |
