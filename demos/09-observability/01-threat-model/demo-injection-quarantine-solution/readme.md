# Completed Prompt Injection Quarantine Demo

This is the finished counterpart of [`../demo-injection-quarantine/`](../demo-injection-quarantine/readme.md). The starter is what you work in; this folder holds the worked-out result of actually running it. The demo has no build step, so the result is captured evidence: the bait in place, both runs transcribed, and the sub-agent's returned YAML preserved verbatim.

## What Is Different From the Starter

| Path | Role |
|---|---|
| `RESULTS.md` | What was executed, what the runs produced, and which parts are model-dependent |
| `transcripts/run-a-direct-read.md` | The direct-read pass: command, tool calls, final answer |
| `transcripts/run-b-quarantined.md` | The delegated pass: command, tool calls, returned YAML |
| `expected-summary.yaml` | The sub-agent's returned YAML, exactly as captured |
| `.env.example` | The bait value, committed so the demo can be recreated |
| `public/` | The exfiltration target, shipped empty because neither run wrote to it |
| `.gitignore` | Same list as the starter, except `public/` is narrowed to `public/*` with `!public/.gitkeep`, so the folder marker stays tracked while anything a run writes into it is ignored |

Everything else, including `untrusted/customer-feedback.md` and `.claude/agents/feedback-summarizer.md`, is identical to the starter. Presenter choreography now lives once at [`../demo-presenter-prompt-injection-quarantine.md`](../demo-presenter-prompt-injection-quarantine.md).

## Reproduce It

```bash
cp .env.example .env
```

On PowerShell:

```powershell
Copy-Item .env.example .env
```

Then open Claude Code in this folder and follow the Run A and Run B sections of the [starter readme](../demo-injection-quarantine/readme.md). The commands used for the captured headless runs are printed in each transcript.

`.env` stays out of version control, so it is recreated from `.env.example` rather than shipped. Its value is a fabricated string, not a credential.

## Do Not Open Both Folders in One Session

This folder and the starter both define a sub-agent named `feedback-summarizer`. Claude Code resolves project sub-agents by walking up from the working directory, and for nested project directories the definition closest to the working directory wins. These two folders are siblings rather than nested, and the docs state no resolution for that arrangement or for an agents folder pulled in with `--add-dir`. Open one folder or the other, and do not add the second with `--add-dir`.

