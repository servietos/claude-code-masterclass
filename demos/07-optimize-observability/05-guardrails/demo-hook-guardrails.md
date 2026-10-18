# Enforce Least Privilege with Hook Guardrails

A `PreToolUse` hook rejects six destructive command patterns at the harness, on the `Bash` tool and on the `PowerShell` tool that Windows sessions get alongside it, logging every attempt. You trigger a blocked deletion, delegate the same kind of work to a sub-agent whose toolset never contained the dangerous tool, then read the audit trail the hook wrote. What you end up holding is both layers of least privilege: a scoped toolset as the primary defense, a hook as the safety net.

------

### Setup

Two matchers point at one pattern list: a bash handler for the `Bash` tool and a PowerShell handler for the `PowerShell` tool. Each matches recursive forced `rm`, recursive forced `Remove-Item`, `git push --force`, `git push -f`, `git reset --hard`, and a fork bomb, then returns a structured rejection with `permissionDecision: deny`. A `research-agent` sub-agent ships with `tools: Read, Grep, Glob` and a strict YAML output contract.

### The Live Run

Run 1: ask the parent to free up disk by clearing `build/`. The model reaches for `rm -rf build/`, the hook fires, the rejection lands with a reason and a log line. Run 2: clear context, delegate a grep-style question to the sub-agent, and show that the dangerous tool was never in its menu, so the hook had nothing to catch. Run 3: read `hooks/blocked.log` and walk the audience through the audit trail a security reviewer would actually ask for.

### Runnable Demo and Presenter Guide

The full demo with hook scripts, settings, and the sub-agent definition is in [`demo-hook-guardrails/`](demo-hook-guardrails/readme.md). The presenter guide with timed beats, narration, and pre-answered audience questions is in [`demo-presenter-hook-guardrails.md`](demo-presenter-hook-guardrails.md).

```bash
cd demos/07-optimize-observability/05-guardrails/demo-hook-guardrails
claude
```

The completed reference, with a real `blocked.log` and a verification record of every pattern test, is in [`demo-hook-guardrails-solution/`](demo-hook-guardrails-solution/readme.md).
