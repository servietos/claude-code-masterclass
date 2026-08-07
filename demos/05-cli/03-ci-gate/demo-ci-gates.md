# Build a Claude-powered lint gate that fails the build on real issues

A sentinel token turns a free-form audit into a binary build signal: the script greps the output for `LINT_PASS` or `LINT_FAIL` and maps it to a shell exit code. You fill in the empty `lint-with-claude.sh` in the [lint-with-claude/](lint-with-claude/) starter (or its `lint-with-claude.ps1` twin), break `slugify` on purpose to watch the gate exit 1, then wire the script into a GitHub Actions workflow. You end holding a read-only audit step that blocks the build on a real issue and exits 2 rather than guessing when the run is ambiguous.

------

## Setup

Start Claude Code in the starter:

```bash
cd demos/05-cli/03-ci-gate/lint-with-claude
npm install
claude
```

Expected result: `npm test` passes on both utilities, which is the clean baseline the audit has to approve in Part A.

## Part A: Write the Sentinel Script

The audit prompt ships in the starter as [lint-with-claude/prompt.txt](lint-with-claude/prompt.txt), so the script reads it instead of writing it:

```text
Audit the codebase in src/ and test/ for code quality and edge cases.
If you find ANY issue, end your response with LINT_FAIL.
If it is perfectly clean, end with LINT_PASS.
```

With the project and the prompt in place, write the audit script:

```text
Write a bash script lint-with-claude.sh that runs Claude headless against the src/ folder.
The script sits in this folder and audits the src/ and test/ folders next to it.
The audit prompt already ships beside the script as prompt.txt, so read it with "$(cat prompt.txt)" and do not write that file.
The script must grep the output for LINT_PASS and LINT_FAIL.
Exit 0 for LINT_PASS, exit 1 for LINT_FAIL, exit 2 for any other outcome.
Use --tools "Read,Glob,Grep" so the audit cannot write files, and --max-turns 10 because a read-only run spends a turn per file it opens.
```

PowerShell:

```text
Write a PowerShell script lint-with-claude.ps1 that runs Claude headless against the src/ folder.
The script sits in this folder and audits the src/ and test/ folders next to it, so it starts with Set-Location $PSScriptRoot.
The audit prompt already ships beside the script as prompt.txt, so read it with (Get-Content prompt.txt -Raw) and do not write that file.
The script must capture the output into a variable and test it with the case-sensitive -cmatch operator, not -match.
Exit 0 for LINT_PASS, exit 1 for LINT_FAIL, exit 2 for any other outcome.
Use --tools "Read,Glob,Grep" so the audit cannot write files, and --max-turns 10 because a read-only run spends a turn per file it opens.
```

`-cmatch` is the load-bearing detail: PowerShell's plain `-match` is case-insensitive, so it would accept a stray `lint_pass` in prose as a verdict. `grep` is case-sensitive by default, which is why the Bash version needs no equivalent flag.

Expected result: a working script that exits 0 on a clean codebase. The audit is a model judgement, so a first run may already report `LINT_FAIL` on a nit; address what it flags before moving to Part B.

## Part B: Trigger a Failure

Introduce a deliberate edge case bug to trigger LINT_FAIL:

```text
Remove the trim() call from slugify so that leading and trailing spaces are not stripped.
Do not update the test file.
```

Run the script and observe the exit code:

```bash
bash lint-with-claude.sh
echo "Exit code: $?"
```

PowerShell:

```powershell
./lint-with-claude.ps1
"Exit code: $LASTEXITCODE"
```

A good outcome is exit code 1 with LINT_FAIL in the output. If you see exit code 2, check that the grep expressions (or the `-cmatch` patterns) match the exact token casing.

## Part C: Wire into GitHub Actions

Add a CI workflow that runs the audit before tests:

```text
Create .github/workflows/ci.yml.
Add a step that runs lint-with-claude.sh before the npm test step.
The audit step must fail the workflow if the script exits non-zero.
Use ubuntu-latest and Node 20.
```

PowerShell: keep the same workflow and give the audit step `shell: pwsh` with `run: ./lint-with-claude.ps1`. The `ubuntu-latest` runner ships PowerShell 7, so the `.ps1` gate needs no Windows runner and no extra install step. A non-zero exit fails the step identically either way.

The completed reference version of this demo (working script, fixed utilities, tests for both functions, and the CI workflow) lives in [lint-with-claude-solution/](lint-with-claude-solution/).
