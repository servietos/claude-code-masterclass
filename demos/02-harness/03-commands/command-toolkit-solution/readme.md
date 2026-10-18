# Command Toolkit Solution

The finished counterpart of `../command-toolkit/`. It contains all four slash commands and the extended grouping map that the demo guide builds step by step.

## Layout

| Path | What it holds |
|------|---------------|
| `src/notes.mjs` | The changelog renderer, with `refactor` added to `GROUPS` |
| `data/commits.json` | 14 fictional conventional-commit entries |
| `test/notes.test.mjs` | `node:test` assertions, including the refactor grouping case |
| `.claude/commands/release-status.md` | Seed command shipped with the starter |
| `.claude/commands/notes-for.md` | Renders and reviews the changelog for a version |
| `.claude/commands/add-commit-type.md` | Extends the grouping map and its test |
| `.claude/commands/audit-commands.md` | Lints every command file for frontmatter gaps |

## Commands

```bash
npm install
npm test
node src/notes.mjs 2.4.0
```

## Command Scope Migration Note

`/release-status`, `/notes-for` and `/add-commit-type` stay in this project's `.claude/commands/` because each one names `src/notes.mjs`, `data/commits.json` or the `GROUPS` map and means nothing outside this repository.

`/audit-commands` is the cross-project candidate: it lints command files against rules that hold in any repository. Its personal-scope destination is `~/.claude/commands/audit-commands.md`.

Promoted from a single file into a skill folder, it would become `~/.claude/skills/audit-commands/SKILL.md` with `name` and `description` frontmatter, and the lint rules would move into supporting files beside it, out of the prompt body.
