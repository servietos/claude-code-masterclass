---
presents: demo-ci-gates.md
budget: 4 min
beats: 4
---

# Present: Build a Claude-powered lint gate that fails the build on real issues

How a model judgement becomes a deterministic exit code, and why the third exit path keeps a broken build from sneaking through. Four beats: the read-only run, the three-way exit block, the deliberate bug, the workflow step.

------

**Shell:** beats quote Bash; [`lint-with-claude.ps1`](lint-with-claude-solution/lint-with-claude.ps1) is the twin, same three exit codes. PowerShell's `-match` is case-insensitive, so beat 2 uses `-cmatch`; beat 4 only adds `shell: pwsh`. Two quoted forms are Windows-fatal: `$?` prints `True`, `< /dev/null` is a parse error.

## Beats

### Beat 1: the prompt is a file, and the run that reads it cannot write (1 min)

**Open:** [`prompt.txt`](lint-with-claude-solution/prompt.txt) · [`src/`](lint-with-claude-solution/src/) · [`test/`](lint-with-claude-solution/test/)
**Say:** The criteria live in a file the team reviews in a pull request. An audit that can edit the code it grades is not an audit.

```text
Audit the codebase in src/ and test/ for code quality and edge cases.
If you find ANY issue, end your response with LINT_FAIL.
If it is perfectly clean, end with LINT_PASS.
```

**Result:** [`lint-with-claude.sh`](lint-with-claude-solution/lint-with-claude.sh), grown from a bare shebang

```bash
echo "Running Claude headless..."
# < /dev/null keeps claude from waiting on stdin when nobody is at the terminal
OUTPUT=$(claude -p "$(cat prompt.txt)" --tools "Read,Glob,Grep" --max-turns 10 < /dev/null)
echo "$OUTPUT"
```

**Gotcha:** `--tools`, not `--allowed-tools`. `< /dev/null` stops the step hanging in a runner.

### Beat 2: three exit codes, because ambiguous output is neither pass nor fail (1 min)

**Open:** [`lint-with-claude.sh`](lint-with-claude-solution/lint-with-claude.sh)
**Say:** CI understands one thing about a step: the number it exited with. Two outcomes are not enough, because a run can also fail to answer at all.

```text
The script must grep the output for LINT_PASS and LINT_FAIL.
Exit 0 for LINT_PASS, exit 1 for LINT_FAIL, exit 2 for any other outcome.
```

**Result:** `LINT_FAIL` ended up tested first

```bash
# the exit code is the CI contract: 1 fails the build, 0 passes it, 2 says the run was unusable
if echo "$OUTPUT" | grep -q "LINT_FAIL"; then
  echo "LINT_FAIL found. Build blocked."
  exit 1
elif echo "$OUTPUT" | grep -q "LINT_PASS"; then
  echo "LINT_PASS found. Build approved."
  exit 0
else
  echo "Indeterminate outcome."
  exit 2
fi
```

**Gotcha:** the order is load-bearing. A response naming both tokens must block, and `else` exits 2 so a timeout is never read as a verdict.

### Beat 3: the failing run is the only proof the gate works (1 min)

**Open:** [`src/slugify.ts`](lint-with-claude-solution/src/slugify.ts) · [`test/slugify.test.ts`](lint-with-claude-solution/test/slugify.test.ts)
**Say:** A gate that has never blocked anything looks exactly like a gate that cannot. Hand it something known to be wrong.

```text
Remove the trim() call from slugify so that leading and trailing spaces are not stripped.
Do not update the test file.
```

```bash
bash lint-with-claude.sh
echo "Exit code: $?"
```

**Result:** exit 1, the finding became a guard, plus three tests the starter did not have

```diff
-    .replace(/-+/g, '-');
+    .replace(/-+/g, '-')
+    .replace(/^-+|-+$/g, '');
```

**Gotcha:** exit 2 means the grep and the prompt disagree on token casing, not a failed audit.

### Beat 4: CI needs nothing new, only an exit code in the right position (1 min)

**Open:** [`.github/workflows/ci.yml`](lint-with-claude-solution/.github/workflows/ci.yml)
**Say:** A step that exits non-zero fails the job whatever produced the number. The one real decision is where in the sequence it sits.

```text
Add a step that runs lint-with-claude.sh before the npm test step.
The audit step must fail the workflow if the script exits non-zero.
```

**Result:** an ordinary shell step ahead of the tests; the starter has no `.github/` at all

```yaml
      - run: npm ci
      - run: npm install -g @anthropic-ai/claude-code
      - run: bash lint-with-claude.sh
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      - run: npm test
```

**Gotcha:** ahead of `npm test` the audit blocks before any artifact exists; behind it, it only grades code that already passes.

## If the room asks

| Question | Answer |
|---|---|
| Why a sentinel token, not the prose? | Phrasing changes between model versions; a token you specified is a protocol. |
| Does the audit write files or reach the network? | No. `--tools` replaces the built-in set. Add `--disallowed-tools "mcp__*"` when MCP servers are connected. |
| What if it flags a nit on clean code? | Expected on a first run. Address it, or narrow the prompt; never weaken the grep. |
| How do I keep CI cost predictable? | `--max-turns` is the ceiling, and the envelope reports `total_cost_usd` per run. |
| Where did the second fix come from? | The same audit caught a digit bug in [`kebab-to-camel.ts`](lint-with-claude-solution/src/kebab-to-camel.ts); no human read the code. |
