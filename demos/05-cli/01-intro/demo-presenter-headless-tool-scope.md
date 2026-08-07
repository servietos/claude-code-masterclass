---
presents: demo-headless-tool-scope.md
budget: 4 min
beats: 4
---

# Present: Run a Headless Agent and Prove Its Tool Scope

A headless run is a program with an envelope and an exit code, and the flag that sounds like a whitelist restricts nothing. Four beats: the JSON envelope, the same write request under `--allowed-tools` then under `--tools`, and the three-flag comparison.

------

**Setup:** no starter and no solution folder. All four commands run in this topic folder against its own [`readme.md`](readme.md), and the only file created is `scoped.txt`, deleted at the end.

## Beats

### Beat 1: the envelope is the contract a script branches on (1 min)

**Open:** [`readme.md`](readme.md#headless-mode-mechanics)
**Say:** An interactive session owns the screen and never exits. Headless mode makes `claude` a program: reads a prompt, works, prints, returns.

```bash
claude -p "List the H2 headings in readme.md, one per line, with no commentary." --tools "Read,Glob,Grep" --max-turns 5 --output-format json
```

**Result:** one JSON object on stdout from an already-exited process

```json
{
  "type": "result",
  "subtype": "success",
  "is_error": false,
  "num_turns": 2,
  "session_id": "1ef515cf-ab16-45b7-b7af-748b6a60454c",
  "total_cost_usd": 1.584339,
  "result": "The Terminal and the CLI\nWhere Headless Mode Fits\n..."
}
```

**Gotcha:** `session_id` and `total_cost_usd` differ every run; the field names do not. `is_error` is what a pipeline branches on.

### Beat 2: `--allowed-tools` grants permission and removes nothing (1 min)

**Open:** [`readme.md`](readme.md#least-privilege-tool-scoping) · the terminal, so the room sees `ls` answer
**Say:** Tool scoping answers two independent questions: what a run may do without stopping to ask, and what it is capable of at all. This flag answers the first.

```bash
claude -p "Create a file named scoped.txt in this folder containing the word hello." --allowed-tools "Read,Glob,Grep" --max-turns 3
```

**Result:** `scoped.txt` exists afterwards, and the run reports having created it

```bash
ls scoped.txt
```

**Gotcha:** a viewer whose `settings.json` forbids writing sees a refusal instead. Same lesson: the outcome came from settings, not from the flag.

### Beat 3: `--tools` withdraws the capability, and the missing file is the proof (1 min)

**Open:** [`readme.md`](readme.md#the-agent-harness-mental-model)
**Say:** A capability the run does not have is the only restriction a prompt cannot argue with. A model saying it cannot do something is a sentence; a missing file is a fact.

```bash
claude -p "Create a file named scoped.txt in this folder containing the word hello." --tools "Read,Glob,Grep" --max-turns 3
```

**Result:** `ls scoped.txt` reports no such file

```text
I can't create that file: this session has no file-writing tool enabled. The only
local tools available to me here are read-only: Read, Glob, and Grep.
```

**Gotcha:** the refusal wording varies between runs; the absent file does not. Same prompt as beat 2, one flag changed, opposite outcome.

### Beat 4: three flags, three different jobs (1 min)

**Open:** [`readme.md`](readme.md#least-privilege-tool-scoping) · the flag comparison table
**Say:** Not three strengths of one setting. Permission, denial and existence are separable concerns, and picking by how strict a name sounds is how the wrong one gets used.

**Result:** beats 2 and 3 ran rows one and three; row two is the one the demo never runs

```markdown
| Flag                               | Effect                                           | Use it for                                          |
| ---------------------------------- | ------------------------------------------------ | --------------------------------------------------- |
| `--allowed-tools "Read,Glob,Grep"` | Pre-approves those tools so they never prompt    | Removing confirmation friction in an unattended run |
| `--disallowed-tools "Bash(rm *)"`  | Denies matching calls, leaves the tool available | Surgical bans on a specific dangerous command       |
| `--tools "Read,Glob,Grep"`         | Makes those the only built-in tools that exist   | A genuinely read-only audit                         |
```

**Gotcha:** all three govern built-in tools only. A run that must not reach MCP servers still needs `--disallowed-tools "mcp__*"` or `--strict-mcp-config`.

## If the room asks

| Question | Answer |
|---|---|
| Then what is `--allowed-tools` for? | Removing confirmation friction, so a scheduled job does not wait on a prompt nobody will answer. |
| Does `--tools ""` disable everything? | Only the built-ins. MCP tools sit outside the flag. |
| If I deny `Write`, is the run read-only? | No. With `Bash` available the agent writes with a shell redirect. |
| Why `--max-turns` on such a small task? | A hard cost ceiling, budgeted against the tool set: a read-only audit spends a turn per file. |
| Where does the exit code come from? | The `claude` process: 0 on success, non-zero on error. |
