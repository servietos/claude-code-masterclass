# Command Toolkit Starter

A dependency-free Node CLI that turns a fixture of conventional commits into a grouped markdown changelog. It exists so you have something real to automate with custom slash commands: run it, extend its grouping map, and lint the command files you write around it.

## Layout

| Path | What it holds |
|------|---------------|
| `src/notes.mjs` | The changelog renderer and its `GROUPS` map |
| `data/commits.json` | 14 fictional conventional-commit entries |
| `test/notes.test.mjs` | `node:test` assertions over the grouping and rendering |
| `.claude/commands/release-status.md` | The one seed slash command, shipped as an anatomy reference |

## Commands

```bash
npm install
npm test
node src/notes.mjs 2.4.0
```

`npm install` is a no-op: the project has zero dependencies, so it works offline.

## What you add

Three more command files under `.claude/commands/`. The demo guide walks through them.
