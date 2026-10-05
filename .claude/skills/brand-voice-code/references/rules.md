# Brand Voice Rules

This file is the single source of truth for quality rules enforced by the `brand-voice` skill. Add or update rules here without touching `skill.md`.

---

## Rule 1 — No Em Dashes in Prose

Em dashes (`—`, `—`, or `--` used as one) are banned in body text. Replace them with the closest correct punctuation based on their role in the sentence.

| Em dash role | Replace with |
|---|---|
| Parenthetical aside enclosed by two dashes | `(...)` |
| Clause continuation ("x — so y") | `,` or `;` |
| Explanation / amplification ("x — y") | `:` |
| Simple pause between clauses | `;` |

**Not affected:** em dashes inside module link text (`[01 — Intro]`) or inside code fences — these are intentional and must not be changed.

**Examples:**

```
Before: "They run in your OS shell — outside the LLM entirely — so they are deterministic."
After:  "They run in your OS shell, outside the LLM entirely, so they are deterministic."

Before: "Clients discover tools by querying the schema—giving you full control."
After:  "Clients discover tools by querying the schema, giving you full control."

Before: "A MEMORY.md index acts as a table of contents — it is always loaded into context."
After:  "A MEMORY.md index acts as a table of contents: it is always loaded into context."
```

---

## Rule 2 — Mermaid Node Labels

Inside Mermaid diagrams, use `<br/>` for a line break, never `\n`, and wrap the label in double quotes.

`\n` is a flowchart-grammar convenience, not a Mermaid-wide one. In `flowchart`/`graph` node labels it does produce a line break on Mermaid 10 and 11, which is why a wrong one can survive review; in `stateDiagram-v2` the same label renders the literal characters `one\ntwo`. `<br/>` behaves identically in both, so it is the only form that is safe to write without checking the diagram type first.

**Pattern to find:** any Mermaid code fence containing `\n` inside `[...]` or `(...)` node syntax.

**Fix:**
```
Before: O[Orchestrator] --> R[Research Agent\nfinds facts]
After:  O[Orchestrator] --> R["Research Agent<br/>finds facts"]
```

Apply to all node styles: `[]`, `()`, `([])`, `[/\]`, `{{}}`.

Do not modify edge labels (`-->|"label"|`) — those do not use `<br/>`.

### Allowed diagram types

Only these types may appear in a `mermaid` fence: `flowchart`, `graph`, `sequenceDiagram`, `stateDiagram-v2`, `erDiagram`, `classDiagram`, `gantt`, `pie`, `gitGraph`, `journey`.

**Banned:** every `-beta` type (`xychart-beta`, `block-beta`, `sankey-beta`, `packet-beta`, `architecture-beta`) plus `quadrantChart`, `timeline`, `mindmap`, `radar`, `treemap`. They need a recent Mermaid runtime, and the VS Code preview extensions the class is read in render them as a blank box or a raw parse error, with no hint that the type is the problem. GitHub rendering the block is not evidence: the reader's previewer is the target.

**Pattern to find:** any `mermaid` fence whose first non-empty line is not one of the allowed types.

**Fix:** a numeric comparison becomes a Markdown table with a bar column of repeated `█` in a code span, scaled so the largest value fills roughly twenty blocks. It renders in every previewer and needs no runtime.

```
Before: xychart-beta / x-axis ["verbose", "caveman"] / bar [1725, 559]
After:  | `CLAUDE.verbose.md` | 1,725 | `████████████████████` |
        | `CLAUDE.caveman.md` |   559 | `██████`               |
```

---

## Rule 3 — Paragraph Length

No paragraph body may exceed 4 sentences. At the 5th sentence, start a new paragraph (blank line before it).

Count only declarative and imperative sentences ending with `.`, `!`, or `?`. Do not count:
- Sentences inside code fences
- Sentences inside blockquotes
- Sentences inside table cells
- List items

When splitting, find the natural break: prefer splitting after a topic shift, not mid-argument. Do not rewrite sentences — only insert the paragraph break.

---

## Rule 4 — Slash Command Tables

Every module README contains a "Helpful Claude Slash Commands" table. Commands in that table must be specific to the module's topic. The same generic set (`/update-config`, `/fewer-permission-prompts`, `/find-skills`, `/init`) must not appear unchanged across every module.

**Do not include `/init` unless the module is explicitly about starting a new project or initializing a `CLAUDE.md`.** Modules where `/init` is appropriate: `01-intro-constitution`, `07-memory`.

### Approved command sets by module topic

| Module topic | Preferred commands |
|---|---|
| Harness intro / settings | `/init`, `/update-config`, `/memory`, `/config` |
| Slash commands | `/review`, `/security-review`, `/cost`, `/help` |
| Hooks | `/update-config`, `/fewer-permission-prompts`, `/doctor` |
| MCP | `/update-config`, `/doctor`, `/find-skills` |
| Skills: intro, skills vs commands | `/find-skills`, `/permissions`, `/mcp` |
| Skills: authoring a skill | `/skills`, `/find-skills`, `/permissions`, `/model` |
| Skills: composite, scripts and references | `/update-config`, `/fewer-permission-prompts`, `/permissions`, `/reload-plugins` |
| Skills: dynamic context and forked subagents | `/context`, `/agents`, `/rewind`, `/permissions` |
| Skills: testing and publishing | `/cost`, `/review`, `/security-review` |
| Skills: evaluation and iteration | `/skills`, `/doctor`, `/context`, `/cost` |
| Plugins | `/update-config`, `/doctor`, `/find-skills` |
| Memory | `/memory`, `/init`, `/update-config` |
| Checkpoints | `/rewind`, `/update-config`, `/clear` |
| Subagents | `/model`, `/cost`, `/find-skills` |
| Planning / Plan Mode | `/model`, `/compact`, `/effort`, `/memory` |
| Optimization / token cost | `/context`, `/usage`, `/compact`, `/memory` |
| CLI / headless execution | CLI invocations, not slash commands (see Rule 5) |

When a module topic is not listed, flag it in the output rather than guessing a command set.

The rule bans a repeated command SET, not a repeated row. Inside one module, individual commands may recur across topics (`/memory` in three topics is fine) as long as each topic's set is distinct and earns its rows.

### Built-in vs custom commands

| Command | Type | Description |
|---|---|---|
| `/help` | built-in | Show available commands and keyboard shortcuts |
| `/clear` | built-in | Clear conversation context |
| `/config` | built-in | Open interactive settings panel |
| `/cost` | built-in | Display token usage and session cost |
| `/doctor` | built-in | Health check on installation, MCP servers, hooks |
| `/memory` | built-in | Open global `CLAUDE.md` for editing |
| `/model` | built-in | Switch active model mid-session |
| `/rewind` | built-in | Restore code, conversation, or both to an earlier prompt (aliases: `/checkpoint`, `/undo`; prefer `/rewind`) |
| `/vim` | built-in | Toggle vim keybindings |
| `/init` | built-in | Generate `CLAUDE.md` for current project |
| `/skills` | built-in | Browse installed skills; `Space` cycles visibility state, `Enter` saves to `.claude/settings.local.json` |
| `/plugin` | built-in | Install and manage plugins and marketplaces |
| `/reload-plugins` | built-in | Reload plugin `hooks/`, `agents/`, and `.mcp.json` without restarting the session |
| `/agents` | built-in | Since v2.1.198, prints a pointer to `.claude/agents/`; it is not a lister or editor |
| `/review` | custom (global) | Structured code review of the current branch |
| `/security-review` | custom (global) | Security audit of branch changes |
| `/update-config` | custom (project) | Edit `settings.json` via guided prompts |
| `/fewer-permission-prompts` | custom (project) | Scan transcripts and build a tool allowlist |
| `/find-skills` | custom (project) | Discover and install agent skills |

---

## Rule 5 — Command Table Headings Match Their Contents

A table headed "Helpful Claude Slash Commands" lists slash commands typed in the REPL (`/review`). A table listing shell invocations (`claude -p ... --output-format json`) is headed "Helpful Claude Code CLI Commands". Mixed contents are split into two tables.

```text
Before: ## Helpful Claude Slash Commands
        | `claude -p "..." --output-format json` | Run headless and emit structured JSON |
After:  ## Helpful Claude Code CLI Commands
        | `claude -p "..." --output-format json` | Run headless and emit structured JSON |
```

---

## Rule 6 — Documentation Links Point at the Current Host

The docs moved to three hosts: Claude Code lives on `code.claude.com/docs/en/*`, API and model docs on `platform.claude.com/docs/en/*`, MCP on `modelcontextprotocol.io`. Old `docs.anthropic.com` paths either 404 or redirect, and a redirect today is a broken link tomorrow.

Every documentation link is checked, not assumed. A plausible-looking nested path is the common failure (`code.claude.com/docs/en/plugins/manifest` is a 404 while `code.claude.com/docs/en/plugins-reference` resolves):

```bash
curl -s -o /dev/null -w "%{http_code} %{url_effective}\n" -L "<url>"
```

Treat anything that is not a direct 200 as a defect: rewrite it to the final URL and re-check.

```text
Before: https://docs.anthropic.com/en/docs/claude-code/hooks
After:  https://code.claude.com/docs/en/hooks
```

---

## Rule 7 — Every Shipped Command Exists in the Installed CLI

Before a command table ships, verify each row against the installed CLI (`claude --help`, `claude -p --help`, and the current docs at `code.claude.com/docs/en/commands`). Removed commands and invented flags are defects, and a removed command described as a live feature is the worst case.

Behaviour changes count as defects too: `/agents` still exists but since 2.1.198 it prints a pointer to `.claude/agents/` instead of opening a management wizard, so any row calling it a lister or editor is wrong. Known confusions: `/permissions` edits session permission rules, not agent frontmatter, and `/cost` is an alias for `/usage`.

When two names exist for the same action (`/usage` and `/cost`), pick one and use it consistently across the module.

```text
Before: | `/agents` | List and edit your sub-agents |
After:  | `/mcp` | Inspect connected MCP servers and their tools |
```

---

## Adding New Rules

When a new quality pattern is discovered during editing:
1. Add a numbered rule section here following the same format.
2. Include a "Before / After" example.
3. Update the skill summary comment in `skill.md` description if the rule type is new.

Do not modify `skill.md` instructions for new rules — the instructions deliberately stay generic ("apply the rules from references/rules.md").
