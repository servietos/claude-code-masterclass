# Configure a qa-agent for browser verification

A qa-agent is a specialized sub-agent scoped exclusively to QA and browser verification: screenshots, Lighthouse audits, viewport checks, console error detection, and interaction testing. It runs in its own isolated context window and carries no implementation authority: it tests, audits, and reports findings back to the orchestrator. The agent wires two MCPs in its frontmatter: `playwright` for browser automation and interaction, and `chrome-devtools` for low-level inspection, performance tracing, and Lighthouse audits.

## The QA Agent File

The agent file lives at [`.claude/agents/playwright-expert.md`](../../../.claude/agents/playwright-expert.md).

```yaml
---
name: playwright-expert
description: >-
  QA and verification specialist. Uses Playwright and Chrome DevTools to take screenshots,
  run Lighthouse audits, verify layout at multiple viewports, check accessibility, and
  diagnose visual bugs. Apply when the task is "verify", "screenshot", "run Lighthouse",
  "check accessibility", "test interactions", or "QA the page". Reports findings only;
  does not write or modify code.
model: haiku
tools: [Read, Bash, Glob, Grep,
        mcp__playwright__browser_navigate, mcp__playwright__browser_take_screenshot,
        mcp__playwright__browser_snapshot, mcp__playwright__browser_click,
        mcp__playwright__browser_hover, mcp__playwright__browser_resize,
        mcp__playwright__browser_evaluate, mcp__playwright__browser_console_messages,
        mcp__playwright__browser_network_requests, mcp__playwright__browser_wait_for,
        mcp__chrome-devtools__lighthouse_audit, mcp__chrome-devtools__take_screenshot,
        mcp__chrome-devtools__performance_start_trace, mcp__chrome-devtools__performance_stop_trace,
        mcp__chrome-devtools__performance_analyze_insight, mcp__chrome-devtools__list_console_messages, ...]
mcpServers:
  playwright:
    type: stdio
    command: npx
    args:
      - "@playwright/mcp@latest"
      - "--vision"
  chrome-devtools:
    type: stdio
    command: npx
    args:
      - "-y"
      - "chrome-devtools-mcp@latest"
disallowedTools: [Write, Edit, NotebookEdit]
---
```

## Playwright MCP vs Chrome DevTools MCP

| Task | MCP |
|---|---|
| Navigate to a URL | `mcp__playwright__browser_navigate` |
| Click a button or link | `mcp__playwright__browser_click` |
| Resize to a breakpoint | `mcp__playwright__browser_resize` |
| Take a screenshot | `mcp__playwright__browser_take_screenshot` |
| Read console errors | `mcp__playwright__browser_console_messages` |
| Run a Lighthouse audit | `mcp__chrome-devtools__lighthouse_audit` |
| Record a performance trace | `mcp__chrome-devtools__performance_start_trace` |
| Inspect network requests | `mcp__chrome-devtools__list_network_requests` |

## Spawning the qa-agent from an Orchestrator

```text
You are an orchestrator. Spawn the following agents in sequence:

1. angular-expert
   Task: Create a standalone UserListComponent in src/app/users/user-list/.
         Fetch users from GET /users using resource(). Use OnPush and signals.
   Return: { "status", "filesChanged", "summary" }

2. playwright-expert
   Task: Navigate to http://localhost:4200/users.
         Verify the component renders at 320px, 768px, and 1280px.
         Run a Lighthouse audit and check the console for errors.
   Return: { "status", "pagesVerified", "viewportsTested", "lighthouseScores", "issues", "summary" }

If the playwright-expert reports issues, spawn angular-expert again with the issue list attached.
```

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/mcp` | Confirm the playwright and chrome-devtools MCP connections are live before spawning the qa-agent |
| `/tasks` | Monitor the playwright-expert running browser verification in the background |
| `/model` | Switch to Haiku for the playwright-expert and compare cost against Sonnet implementation agents |
| `/effort` | Lower the effort level for repetitive screenshot-and-audit loops to reduce per-task cost |

## Key Topics covered in this module

- [Claude Code Sub-Agents](https://code.claude.com/docs/en/sub-agents): agent frontmatter fields, tool allowlists, and permission blocks
- [Claude Models Overview](https://platform.claude.com/docs/en/about-claude/models/overview): when to use Haiku versus Sonnet for cost-efficient agent networks
- [Playwright MCP](https://github.com/microsoft/playwright-mcp): browser automation tools for navigation, interaction, and screenshot capture
- [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp): Lighthouse audits, performance traces, and network inspection via Chrome DevTools Protocol
