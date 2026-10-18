# Build a Claude-powered lint gate that fails the build on real issues

A sentinel token turns a free-form audit into a binary build signal: the script greps the output for `LINT_PASS` or `LINT_FAIL` and maps it to a shell exit code. You fill in the empty `lint-with-claude.sh` in the [lint-with-claude/](lint-with-claude) starter (or its `lint-with-claude.ps1` twin), break `slugify` on purpose to watch the gate exit 1, then wire the script into a GitHub Actions workflow.

------

Work in [lint-with-claude/](lint-with-claude) after `npm install`; the completed reference is in [lint-with-claude-solution/](lint-with-claude-solution).

## Part A: Write the Sentinel Script

The audit prompt ships in the starter as [lint-with-claude/prompt.txt](lint-with-claude/prompt.txt) and ends every audit with `LINT_PASS` or `LINT_FAIL`, so the script only reads it and maps the token to an exit code.

```text
Write a bash script lint-with-claude.sh that runs Claude headless against the src/ folder.
The script sits in this folder and audits the src/ and test/ folders next to it.
The audit prompt already ships beside the script as prompt.txt, so read it with "$(cat prompt.txt)" and do not write that file.
The script must grep the output for LINT_PASS and LINT_FAIL.
Exit 0 for LINT_PASS, exit 1 for LINT_FAIL, exit 2 for any other outcome.
Use --tools "Read,Glob,Grep" so the audit cannot write files, and --max-turns 10 because a read-only run spends a turn per file it opens.
```

```text
Write a PowerShell script lint-with-claude.ps1 that runs Claude headless against the src/ folder.
The script sits in this folder and audits the src/ and test/ folders next to it, so it starts with Set-Location $PSScriptRoot.
The audit prompt already ships beside the script as prompt.txt, so read it with (Get-Content prompt.txt -Raw) and do not write that file.
The script must capture the output into a variable and test it with the case-sensitive -cmatch operator, not -match.
Exit 0 for LINT_PASS, exit 1 for LINT_FAIL, exit 2 for any other outcome.
Use --tools "Read,Glob,Grep" so the audit cannot write files, and --max-turns 10 because a read-only run spends a turn per file it opens.
```

Expected result: a working script that exits 0 on a clean codebase. The audit is a model judgement, so a first run may already report `LINT_FAIL` on a nit; address what it flags before moving to Part B.

`-cmatch` is the load-bearing detail: PowerShell's plain `-match` is case-insensitive, so it would accept a stray `lint_pass` in prose as a verdict.

## Part B: Trigger a Failure

Introduce a deliberate edge case bug, then run the script and observe the exit code.

```text
Remove the trim() call from slugify so that leading and trailing spaces are not stripped.
Do not update the test file.
```

```bash
bash lint-with-claude.sh
echo "Exit code: $?"
```

```powershell
./lint-with-claude.ps1
"Exit code: $LASTEXITCODE"
```

A good outcome is exit code 1 with `LINT_FAIL` in the output. If you see exit code 2, check that the grep expressions (or the `-cmatch` patterns) match the exact token casing.

The failing run is the proof the gate works: a gate that has never blocked anything looks exactly like a gate that cannot.

## Part C: Wire into GitHub Actions

Add a CI workflow that runs the audit before tests. For the PowerShell gate, give the audit step `shell: pwsh` with `run: ./lint-with-claude.ps1`; the `ubuntu-latest` runner ships PowerShell 7.

```text
Create .github/workflows/ci.yml.
Add a step that runs lint-with-claude.sh before the npm test step.
The audit step must fail the workflow if the script exits non-zero.
Use ubuntu-latest and Node 20.
```

Expected result: a `.github/workflows/ci.yml` whose audit step runs as an ordinary shell step ahead of `npm test`, as in the [solution's `ci.yml`](lint-with-claude-solution/.github/workflows/ci.yml).

A non-zero exit fails the step identically in either shell, so the audit blocks the build before any test runs.
