# Memory Architectures Solution

Completed reference for [`lab-03-memory-architectures.md`](../../lab-03-memory-architectures.md). The starter you work in lives beside this folder as [`memory-lab/`](../memory-lab/readme.md).

## What is here

| Path | Role |
|---|---|
| `notes/topic-*.md` | The eight-note Lumen corpus, 200 to 400 words each |
| `notes/STATE.md` | The Step 2 condensed statefile, 509 words |
| `recall-questions.txt` | The three recall questions used against all four architectures |
| `.mcp.json` | The minimal memory server registration the lab prints first, before the `MEMORY_FILE_PATH` fix below |
| `mcp-probe.js` | Drives the memory server over stdio without Claude Code, to prove the server and its tools |

## Measured corpus size

Token counts with `tiktoken` `cl100k_base`:

| Item | Tokens |
|---|---|
| Eight notes loaded in full | 2859 |
| `notes/STATE.md` | 917 |
| `recall-questions.txt` | 70 |

The in-context architecture therefore costs about 2,900 tokens for this corpus, which is where the lab's 2,500 to 5,000 band comes from: at 200 to 400 words per note, eight notes bound the corpus at roughly those two numbers. The statefile lands at 917 tokens, about a third of the corpus.

## Verifying the memory server without Claude Code

```bash
npm view @modelcontextprotocol/server-memory version
node mcp-probe.js "$PWD/memory.jsonl"
```

Measured on 2026-07-24: npm version `2026.7.4`, not deprecated; the running server reports `serverInfo.name` `memory-server` and `serverInfo.version` `0.6.3`, protocol `2025-06-18`, and startup line `Knowledge Graph MCP Server running on stdio`.

The nine tools it exposes:

| Tool | Kind |
|---|---|
| `create_entities` | write |
| `create_relations` | write |
| `add_observations` | write |
| `delete_entities` | destructive |
| `delete_observations` | destructive |
| `delete_relations` | destructive |
| `read_graph` | read only |
| `search_nodes` | read only |
| `open_nodes` | read only |

The four tools the lab names (`create_entities`, `create_relations`, `search_nodes`, `read_graph`) all exist.

## Where the graph is stored

The minimal `.mcp.json` sets no `MEMORY_FILE_PATH`, so the server writes `memory.jsonl` inside its own package directory in the npx cache. That store is shared by every project that starts the server the same way, and it disappears when the npx cache is cleared. To keep the graph with the lab, set an absolute path:

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": { "MEMORY_FILE_PATH": "D:/path/to/memory-lab/memory.jsonl" }
    }
  }
}
```

A relative `MEMORY_FILE_PATH` is resolved against the server's own directory, not the project, so it has to be absolute.

## Where the auto-memory store is written

Auto-memory is on by default and its directory is derived from the git repository, not from the folder the session was launched in, so an unpinned run inside this lab files its memories in the course repo's own store at `~/.claude/projects/<project>/memory/`. Step 4 pins it into the lab with `.claude/settings.json`:

```json
{
  "autoMemoryEnabled": true,
  "autoMemoryDirectory": "D:/path/to/memory-lab/auto-memory"
}
```

The value must be absolute or start with `~/`, the same constraint as `MEMORY_FILE_PATH` above, and a project-scoped `autoMemoryDirectory` is honoured only after the workspace trust dialog is accepted. `MEMORY.md` in that directory is the file loaded at every session start, capped at the first 200 lines or 25KB; the topic files beside it are read only on demand.

## Not reproduced here

Steps 1 to 6 of the lab produce `results/*.md` from live Claude Code sessions (in-context run, statefile run, graph run, auto-memory run, comparison, audit), so they are not reproduced here. Neither is the `auto-memory/` store itself: Claude Code writes those files during the session and chooses their contents, so a checked-in copy would be someone else's write policy rather than the learner's. The lab's Step 6 is built on `read_graph`, which this server really exposes; `/graphify` is deliberately not used anywhere, because it is not a real command: not built in, not in this repo's skills, not in the installed marketplaces.
