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

**Open:** [`prompt.txt`](lint-with-claude-solution/prompt.txt) · [`src/`](lint-with-claude-solution/src) · [`test/`](lint-with-claude-solution/test)
**Say:** The criteria live in a file the team reviews in a pull request. An audit that can edit the code it grades is not an audit.

```text
Audit the codebase in src/ and test/ for code quality and edge cases.
If you find ANY issue, end your response with LINT_FAIL.
If it is perfectly clean, end with LINT_PASS.
```

**Result:** [`lint-with-claude.sh`](lint-with-claude-solution/lint-with-claude.sh), grown from a bare shebang

```bash
output=$(claude -p "$(cat prompt.txt)" --tools "Read,Glob,Grep" --max-turns 10)
status=$?
printf '%s\n' "$output"
```

**Gotcha:** the flag is `--tools`, which replaces the built-in tool set. Add `< /dev/null` to the `claude` call when a runner step hangs waiting on stdin.

### Beat 2: three exit codes, because ambiguous output is neither pass nor fail (1 min)

**Open:** [`lint-with-claude.sh`](lint-with-claude-solution/lint-with-claude.sh)
**Say:** CI understands one thing about a step: the number it exited with. Two outcomes are not enough, because a run can also fail to answer at all.

```text
The script must grep the output for LINT_PASS and LINT_FAIL.
Exit 0 for LINT_PASS, exit 1 for LINT_FAIL, exit 2 for any other outcome.
```

**Result:** a token counts as a verdict only when exactly one of the two appears

```bash
pass=0
fail=0
# Match each verdict token anywhere in the response
printf '%s' "$output" | grep -q 'LINT_PASS' && pass=1
printf '%s' "$output" | grep -q 'LINT_FAIL' && fail=1
# Exactly one token is a verdict; zero or both is an outcome the gate cannot act on
if [ "$pass$fail" = "10" ]; then
  exit 0
fi
if [ "$pass$fail" = "01" ]; then
  exit 1
fi
exit 2
```

**Gotcha:** a response naming both tokens exits 2, so it never passes. A non-zero exit from `claude` (timeout, turn cap) also returns 2 before any grep runs.

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

**Result:** exit 1, and the audit's reply ends with the verdict token

```text
LINT_FAIL
Exit code: 1
```

**Gotcha:** exit 2 means the output carried no single verdict token: check the token casing, or whether `claude` finished before it wrote one.

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
| Why match a sentinel token at all? | Phrasing changes between model versions; a token you specified is a protocol. |
| Does the audit write files or reach the network? | No. `--tools` replaces the built-in set. Add `--disallowed-tools "mcp__*"` when MCP servers are connected. |
| What if it flags a nit on clean code? | Expected on a first run. Address it, or narrow the prompt; never weaken the grep. |
