# Harden Newsletter, Lab Solution

The completed reference for `lab-03-harden-newsletter.md`. The starter beside this folder stays pristine; everything here is the finished wiring.

## What Is Here

```text
harden-newsletter-solution/
├── readme.md
├── .gitignore
├── .env.example
├── .claude/
│   ├── settings.json
│   └── agents/
│       ├── feedback-summarizer.md
│       ├── drafting-agent.md
│       └── publish-agent.md
├── hooks/
│   ├── deny-destructive.ps1
│   ├── budget-cap.ps1
│   ├── deny-destructive-guide-literal.ps1
│   └── budget-cap-guide-literal.ps1
├── untrusted/
│   └── customer-feedback.md
└── data/
    └── customers.csv
```

## Hook Contract

`deny-destructive.ps1` and `budget-cap.ps1` return the documented PreToolUse decision shape on stdout and exit 0:

```json
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"..."}}
```

Exit code 2 also blocks a PreToolUse call, but on exit 2 stdout is discarded and only stderr reaches the model, so a reason written to stdout never arrives. The two `*-guide-literal.ps1` scripts keep the older `{"decision":"block"}` plus exit 2 form as a counter-example: they block the command but the reason never reaches Claude. The lab guide now teaches the `hookSpecificOutput` form above.

Both scripts resolve their paths from `$PSScriptRoot`, so `blocked.log` and `session-counter.txt` land in `hooks/` no matter which directory the hook runs from. `session-counter.txt` is keyed by `session_id`, so a new session starts at zero instead of inheriting the previous session's cap.

`settings.json` matches on `Bash|PowerShell` because `Remove-Item` arrives through the PowerShell tool, not the Bash tool.

## Verify the Hooks

```bash
echo '{"session_id":"s1","hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"rm -rf ."}}' | pwsh -NoProfile -File ./hooks/deny-destructive.ps1
```

```powershell
'{"session_id":"s1","hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"rm -rf ."}}' | pwsh -NoProfile -File ./hooks/deny-destructive.ps1
```

## Before You Start

```bash
cp .env.example .env
```

```powershell
Copy-Item .env.example .env
```
