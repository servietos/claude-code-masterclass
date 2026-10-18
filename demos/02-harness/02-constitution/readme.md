# Write the CLAUDE.md Constitution

Without a `CLAUDE.md`, every session opens by re-explaining the same project:

```text
We use Angular 21 with signals and standalone components, .NET 10 for the API, and
the EF Core migrations live under src/Api/Migrations. Never edit generated files.
Now add a health endpoint and wire it into the existing controller pattern.
```

With that context in `CLAUDE.md`, the same request is one line, and every teammate who checks out the repo gets the same behavior:

```text
Add a health endpoint to the API.
```


## CLAUDE.md: The Project Constitution

Context engineering is the practice of deciding what Claude sees, what it remembers, and what it can reference, before and during a session. The quality of Claude's output is directly tied to the quality of its context: the right files, the right instructions, and the right level of detail at the right time.

CLAUDE.md is a markdown file that Claude reads automatically at the start of every session. It is the primary mechanism for encoding persistent, project-level instructions: coding conventions, architectural decisions, test strategies, deployment notes, and anything else Claude should know without being told each time.

Think of it as a standing brief for a new engineer joining the project. The file is checked into the repository, so the same instructions apply to every developer and every CI run that uses Claude Code.

```markdown
# CLAUDE.md

## Hard rules

- YOU MUST NOT commit or push without explicit user request.
- YOU MUST NOT add `Co-Authored-By: Claude` to any commit message.
- Code fences must declare a language (`bash`, `python`, `json`, …).
- If a quality check fails, fix the underlying issue. Do not bypass with `--no-verify`.

## Architecture map

- `src/api/`: HTTP handlers only, no business logic
- `src/services/`: all domain logic lives here
- `src/db/`: EF Core migrations and DbContext

## Workflow preferences

- Small fixes → minimal diff. Do not rewrite a section to fix a typo.
- All new features require a unit test alongside the implementation.
- Run `npm test` before marking any task done.

## Token Efficiency

- Never re-read files you just wrote or edited.
- Batch related edits into single operations.
- Do not summarize what you just did unless the result is ambiguous.
```

## CLAUDE.md File Locations

Claude reads CLAUDE.md files from multiple locations and merges them in order of precedence. Understanding the hierarchy lets you share global preferences across all projects while keeping project-specific rules isolated.

- `~/.claude/CLAUDE.md`: global instructions that apply to every project on your machine
- `<project-root>/CLAUDE.md`: project-level instructions, checked into the repository
- `<subfolder>/CLAUDE.md`: scoped instructions for a specific part of the codebase (e.g., `docs/CLAUDE.md` for documentation conventions)

The project root CLAUDE.md is the most commonly used layer. The global file is the right place for personal preferences (preferred shell, editor, or response style) that you want across all workspaces.

## File Mentions

File mentions are the inline way to pull specific files into the active context window. Type `@` followed by a path to attach any file to your message; Claude will read it as part of the prompt rather than having to discover it through tool calls.

```text
@src/services/auth.ts Why does this function re-fetch the user on every request?
```

File mentions work for source files, config files, logs, and even images. They are useful when you want to direct Claude's attention to a specific file without describing its contents: the file speaks for itself.

## Examples That Pin the Output Shape

Prose rules describe intent; examples remove ambiguity. When a project has a recurring output shape (a pagination envelope, a log line, a commit message format), two complete input/output pairs in CLAUDE.md do more than a paragraph describing it. Without them Claude will invent a plausible variant, and plausible variants differ between sessions and between teammates.

The examples belong under `## Conventions` and must use the exact field names and types the real code uses, because Claude copies what it sees rather than what the surrounding sentence claims.

```markdown
## Conventions

### Pagination shape

Every paginated endpoint returns this shape. No exceptions.

GET /todos?page=2&size=10

{ "data": [ ... ], "page": 2, "size": 10, "total": 47, "hasNext": true }

GET /users?page=1&size=5

{ "data": [ ... ], "page": 1, "size": 5, "total": 3, "hasNext": false }

`hasNext` is `page * size < total`, computed from the total count.
```

Two examples beat one, because a single example leaves the model guessing which parts are the pattern and which are the data. The second example varies the values while holding the shape fixed, which is what makes the shape readable as the rule.

## Include, Exclude, Compress

Beyond CLAUDE.md and file mentions, Claude Code gives you three levers for controlling context size. You can include additional files and directories explicitly, exclude noisy paths (build outputs, lock files, generated assets) so they never appear in tool results, and compress long conversations with `/compact` when the context window fills up. These three mechanisms (include, exclude, compress) keep sessions fast and focused as projects grow.

## Path-Scoped Rules

`CLAUDE.md` is unconditional: whatever it says loads on every turn in its directory subtree. That is the right shape for architecture context and team standards, and the wrong shape for a convention that applies to a fraction of the files. Putting PCI logging rules in the root `CLAUDE.md` of a monorepo means every developer working on the unregulated app carries them for nothing.

Rules solve the scoping problem. A rule is a Markdown file under `.claude/rules/` whose YAML frontmatter names the paths it applies to, and Claude Code loads it only when it touches a matching file.

```markdown
---
paths: ["apps/retail/**/*.ts", "apps/corporate/**/*.ts"]
---

# PCI-DSS Logging

Never log a full PAN. Mask to the last four digits at the call site,
not in the log sink.
```

The glob is matched against the file path, so scope by whatever the naming convention actually encodes. Public API routes named `*public.route.ts` and scattered across dozens of domain folders are reachable with `["**/*public.route.ts"]`; scoping by directory instead would miss every one of them.

| Need | Mechanism |
|---|---|
| Applies to the whole project | Root `CLAUDE.md` |
| Applies to one subtree | Nested `CLAUDE.md` in that directory |
| Applies to files matching a pattern, wherever they live | `.claude/rules/<name>.md` with `paths:` frontmatter |

There is no `exclude:` counterpart, so express the scope positively. Naming the paths that should carry the rule is both more precise and cheaper than loading it everywhere and asking Claude to check the filename before applying it.

A rule without `paths:` frontmatter loads at session start, exactly like `.claude/CLAUDE.md`. That makes `.claude/rules/` the place to split a long `CLAUDE.md` into topic files such as `testing.md` or `deploy.md`. Personal rules go in `~/.claude/rules/` and apply to every project on your machine.

When a path-scoped rule never seems to apply, register an `InstructionsLoaded` hook. It logs every `CLAUDE.md` and rules file as Claude Code loads it, with when and why, so you can see whether the glob ever matched.

## Output Styles

`CLAUDE.md` and rules change what Claude knows. An output style changes how it answers, and it is the only harness file that edits the system prompt itself rather than adding a message after it. Reach for one when you keep re-prompting for the same voice or format every turn: replies that lead with a diagram, replies that never speculate, replies that stop at what changed.

A style is a Markdown file with frontmatter, saved at user scope in `~/.claude/output-styles/`, at project scope in `.claude/output-styles/`, or shipped by a plugin.

```markdown
---
name: Answer Only
description: Reply with what changed and what blocks the user, nothing else
keep-coding-instructions: true
---

Say what changed and where, and anything that blocks the user or is theirs to decide.

Do not include how you verified it, what you ruled out, caveats they did not raise,
or next steps. When you are holding detail that might matter, offer it in one clause
and stop.
```

| Field | Effect |
|---|---|
| `name` | The name shown in the picker. Defaults to the file name. |
| `description` | One line describing the style, shown beside the name. |
| `keep-coding-instructions` | Defaults to `false`, which **drops** Claude Code's built-in software engineering instructions. Set it to `true` whenever the style changes tone or format but the work is still coding. |

That default is the trap. A style written to shorten replies, saved without `keep-coding-instructions: true`, also removes the instructions covering how Claude scopes a change, comments code, and verifies its work. Leave it out only when the session is not software engineering at all, such as a writing or data-analysis assistant.

Activate a style with `/config`, which writes `outputStyle` into `.claude/settings.local.json`, or set the field directly in any settings file to choose the scope yourself:

```json
{
  "outputStyle": "Answer Only"
}
```

The system prompt is read once at session start, so a new style or an edit to an active one takes effect after `/clear` or in the next session, never mid-conversation. Styles apply to the main conversation only: a subagent runs its own system prompt and is unaffected, while a fork inherits the parent's.

Four built-in styles ship with Claude Code. **Default** is the standard engineering prompt. **Proactive** executes immediately and makes reasonable assumptions instead of pausing on routine decisions. **Explanatory** adds educational insights alongside the work, and **Learning** goes further by leaving `TODO(human)` markers for you to implement.

| Mechanism | How it reaches the model | Use it when |
|---|---|---|
| Output style | Modifies the system prompt | You want a different tone or response format every turn |
| `CLAUDE.md` | Adds a user message after the system prompt | Claude should always know your project conventions |
| `--append-system-prompt` | Appends to the system prompt for one invocation | You need a one-off addition to a single run |

## Helpful Claude Slash Commands

| Command | Usage |
|---------|-------|
| `/init` | Scaffold a new `CLAUDE.md` in the current repo with architecture and rules. |
| `/memory` | Open the `CLAUDE.md` files Claude loads, to read or edit what is in each layer. |
| `/config` | Open the interactive settings panel to manage preferences and model selection. |

## Key Topics Covered in This Module

- [CLAUDE.md Memory](https://code.claude.com/docs/en/memory): how context files are discovered and merged
- [Slash Commands](https://code.claude.com/docs/en/slash-commands): built-in and custom command authoring
- [Output Styles](https://code.claude.com/docs/en/output-styles): frontmatter fields, the four built-in styles, and how a style differs from `CLAUDE.md`
- [Claude Code: context management](https://code.claude.com/docs/en/overview)
