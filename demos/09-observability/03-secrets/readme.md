# Secure Secrets and Credentials

## How Credentials Leak in a Multi-Agent World

A single-agent setup has one obvious place where credentials live: the environment of the process running Claude Code. The moment you spawn sub-agents, the question becomes much messier because each sub-agent inherits the parent's environment by default and any tool the sub-agent calls can read those variables. A research sub-agent told to "summarize this webpage" should not be able to read `STRIPE_SECRET_KEY`, but in a naive setup it can.

## Cross-Agent Credential Leakage

There are three realistic leakage paths to plan for. First, environment inheritance: sub-agents see what the parent sees unless you explicitly strip variables. Second, tool output: a `printenv` or `env` call dumps everything into context, where injection-style content can then exfiltrate it. Third, MCP server config: secrets baked into `.mcp.json` are visible to every agent that loads that MCP.

This repository is its own worked example of the third path. The `ssh-mcp` entry in `.mcp.json` passes `--password=<value>` and `--sudoPassword=<value>` as literal command arguments, so a git-tracked config file carries shell-level access to a host and every agent that loads the server inherits it. Move both values to environment variables the server reads or to a secret store, and treat anything already committed as compromised.

The first path is the uncomfortable one, because Claude Code has no per-sub-agent environment stripping today. The `env` setting is a flat map applied to every session and to every subprocess spawned from it, and sub-agent frontmatter has no env field at all:

```json
{
  "env": {
    "READ_ONLY_TOKEN": "rot-scoped-to-reads-only"
  }
}
```

So the mitigation is upstream of the harness: keep the high-value secret out of the launching process's environment entirely. Put only the narrowest token the work actually needs into `env`, and issue it from a secret store or a short-lived broker. A deployment agent gets a 60-minute deploy token; a research agent gets nothing; a frontend agent gets a build-time public key, not the production secret.

## Where Secrets Should and Should Not Live

| Place | Verdict | Why |
|---|---|---|
| Inline in `.claude/` files | Never | The directory is git-tracked and copy-pasted between machines |
| Environment variable on the host | Acceptable for dev, scoped per-agent | Easy to scope, easy to rotate |
| `.env` loaded by the harness | Acceptable, gitignored | Same as above with file storage |
| OS keychain or cloud secret store | Preferred for shared and production | Audited access, rotation, no plaintext at rest |
| Managed Agents sandbox | Preferred when on the hosted runtime | Each session gets its own managed sandbox, so nothing you inject crosses back to your laptop |

## The Rotation Habit

Treat any credential that has been in an agent's environment as eventually compromised. Rotate on a fixed cadence, rotate immediately after a suspected injection, and prefer short-lived tokens issued by a broker over long-lived keys. A 60-minute deploy token forgives a lot of mistakes that a multi-year API key does not.

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/mcp` | Inspect MCP server configs so any secret pinned in `.mcp.json` is visible and can be moved to a secret store |
| `/context` | See what is loaded into the window, so a secret pasted into context is spotted before it is sent again |
| `/permissions` | Block tools like `printenv` or shell pipes that could surface environment variables into tool output |

## Key Topics covered in this module

- [Environment and Settings](https://code.claude.com/docs/en/settings): the `env` map, which reaches every session and every subprocess spawned from it
- [Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview): the hosted runtime, where each session runs in an Anthropic-managed sandbox
- [Security Best Practices](https://code.claude.com/docs/en/security): credential hygiene checklist and rotation guidance
