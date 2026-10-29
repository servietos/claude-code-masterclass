# CI/CD Project Specifics

Everything in `.claude/agents/github-devops-agent.md` that is bound to this repository rather than to deploying containers on an Ubuntu host. The agent definition stays portable; this file carries the coupling.

## MCP servers this agent depends on

Declared in the agent frontmatter, resolved from the repo's `.mcp.json`:

| Server | Transport | Used for |
| ------ | --------- | -------- |
| `ssh-mcp` | stdio, configured in `.mcp.json` | Held SSH connection to the configured host, carries the sudo password, returns structured results |
| `chrome-devtools` | stdio, `npx -y chrome-devtools-mcp@latest` | Post-deploy screenshot and console/network evidence |
| `github` | http, `https://api.githubcopilot.com/mcp/` | Structured workflow run logs, failing-step triage, cross-run comparison |

## The ssh-mcp host pin

`ssh-mcp` is pinned to one host: `.mcp.json` reads it from the `SSH_HOST` user environment variable, beside `SSH_USER` and `SSH_PASSWORD`; the deployment manifest names the host asked for. Compare them before the first command and stop if they disagree. An MCP call landing on the wrong box is the one failure no later check catches, because every check then runs on the wrong box too. Confirm on the connection itself (`hostname`, `hostname -I`), never by trusting the variable or the manifest.

Fall back to `ssh` and `scp` for any other host, for file transfer, and when the server is not connected.

## Where the command allowlist is actually enforced

The agent's six-verb scope (`ssh`, `scp`, `docker`, `gh`, `git`, `ls`) is a rule kept, not a fence built. Subagent frontmatter has no `permissions` field, so command-level rules bind only from this project's `.claude/settings.json`; a `permissions:` block in the agent file would look like a boundary and enforce nothing.

Nor does it reach the host: `Bash(ssh:*)` still runs anything on the far side. The guardrail there is the deploy user's own privileges. Scope the remote account; never assume local rules travel over the wire.

## Delegation roster (strict)

| Task | Target |
| ---- | ------ |
| Azure control plane, SWA, App Service, ACR, Bicep, OIDC/WIF | Hand back. `.claude/skills/azure/SKILL.md` owns it |
| App code changes needed for the deploy to work | Hand back to `dotnet-expert` or `angular-expert` |
| Post-deploy page evidence beyond a screenshot | `playwright-expert`, on explicit request only |

Rule: a deploy blocked by app code is reported, never fixed here.

## Skills available in this repo

Check `.claude/skills/<name>/SKILL.md` for a matching convention BEFORE implementing, and prefer its guidance over improvising. Descriptions are in `CLAUDE.md`.

`agentic-seo`, `angular-conventions`, `azure`, `brand-voice-code`, `class-dashboard`, `code-reviewer`, `create-module-pptx`, `dotnet-conventions`, `hook-caveman-compression`, `mermaid-expert`, `microsoft-agent-framework`, `track-time`, `ui-ux-pro-max`
