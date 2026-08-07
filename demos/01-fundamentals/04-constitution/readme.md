# Write a CLAUDE.md Constitution

Context engineering is the practice of deciding what Claude sees, what it remembers, and what it can reference, before and during a session. The quality of Claude's output is directly tied to the quality of its context: the right files, the right instructions, and the right level of detail at the right time.

## CLAUDE.md: The Project Constitution

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

## Helpful Claude Slash Commands

| Command | Usage |
|---------|-------|
| `/memory` | Open the `CLAUDE.md` files Claude loads, to read or edit what is in each layer |
| `/help` | Show available slash commands and their descriptions |

## Include, Exclude, Compress

Beyond CLAUDE.md and file mentions, Claude Code gives you three levers for controlling context size. You can include additional files and directories explicitly, exclude noisy paths (build outputs, lock files, generated assets) so they never appear in tool results, and compress long conversations with `/compact` when the context window fills up. These three mechanisms (include, exclude, compress) keep sessions fast and focused as projects grow.

## Key Topics covered in this module

- [Claude Code: CLAUDE.md documentation](https://code.claude.com/docs/en/memory)
- [Claude Code: context management](https://code.claude.com/docs/en/overview)
- [Claude Code in Action course](https://anthropic.skilljar.com/claude-code-in-action/303241)
