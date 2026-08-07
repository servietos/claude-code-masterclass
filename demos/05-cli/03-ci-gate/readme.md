# Gate CI Pipelines with Sentinel Tokens

Continuous integration pipelines need binary signals: pass or fail. Claude's free-form text output is not binary by default, but sentinel tokens turn it into one. The pattern is simple: instruct Claude to end its response with a specific token (`LINT_PASS` or `LINT_FAIL`), then grep the output in your shell script. The grep result maps to a shell exit code, and the exit code maps to a build gate.

## Why Sentinel Tokens

Parsing AI output with regex is brittle. Model responses change phrasing across versions, and grepping for substrings like "no issues found" breaks the moment the model adds a qualifier. Sentinel tokens are different because they are a protocol you define. The model is instructed to produce exactly `LINT_PASS` or `LINT_FAIL` at the end of its response with no ambiguity about format. Your script greps for the exact token, not for intent.

The third exit path matters too. If Claude times out, hits a token limit, or produces an unexpected response, your script should exit with a code that is neither pass nor fail. Pipelines that treat ambiguous output as pass silently allow bad builds through; pipelines that treat it as fail create noisy false positives. The three-outcome model (pass / fail / indeterminate) is the production-grade version of this pattern.

## Wiring Claude into a CI Workflow

A CI-gate script has four responsibilities: read the audit prompt from the file that ships beside it, run Claude headless against that prompt, capture the output, and grep for the sentinel. Scope the run with `--tools "Read,Glob,Grep"` so an audit that has no business writing files physically cannot. Budget `--max-turns` against the tool set rather than picking a round number: a read-only audit spends one turn per file it opens, so the four-file project here needs ten where a run with shell access would finish in five.

Once the script exits correctly, the CI system treats it as any other step. GitHub Actions, GitLab CI, and Jenkins all respond to shell exit codes. Placing the Claude step before the build step means a failing audit blocks the build before any artifact is produced. Placing it after tests means the audit runs only on code that already passes automated checks.

## Helpful Claude Code CLI Commands

| Command | Usage |
|---|---|
| `claude -p "$(cat prompt.txt)" --tools "Read,Glob,Grep" --max-turns 10` | Run a genuinely read-only audit with a file-based prompt and a tight turn cap. |
| `claude -p (Get-Content prompt.txt -Raw) --tools "Read,Glob,Grep" --max-turns 10` | The same read-only audit in PowerShell, where `Get-Content -Raw` replaces the `$(cat ...)` substitution. |
| `claude -p "prompt" --output-format json \| jq '.result'` | Extract just the model's text from the JSON envelope for cleaner grepping. |
| `claude -p "prompt" --output-format json \| ConvertFrom-Json \| Select-Object -ExpandProperty result` | The same extraction in PowerShell, with no `jq` needed on the machine. |

## Key Topics Covered in This Module

- [GitHub Actions workflow commands](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/workflow-commands-for-github-actions): how exit codes from shell steps propagate to workflow status
- [Claude CLI reference](https://code.claude.com/docs/en/cli-reference): `--tools`, `--allowed-tools`, and `--output-format` flag documentation
