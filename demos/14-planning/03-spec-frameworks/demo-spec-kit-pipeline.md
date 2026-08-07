# Run a Feature Through the Four-Step Spec Kit Pipeline

Take the same tag-search feature you planned by hand and push it through Spec Kit's enforced pipeline: constitution, specify, plan, tasks, implement. You finish with a `specs/` tree you can hold next to your own STATE.md and compare.

------

## Setup

Run [setup-speckit.ps1](setup-speckit.ps1) on Windows, or [setup-speckit.sh](setup-speckit.sh) elsewhere, before the session starts. It leaves a prepared run folder at `~/spec-runs/notes-cli-speckit`, outside this checkout because Spec Kit initialises its own git repository. Pass a path as the first argument to put it somewhere else.

```powershell
.\setup-speckit.ps1
```

Then start the session where the script tells you to:

```powershell
cd $HOME\spec-runs\notes-cli-speckit
claude
```

Spec Kit installs as **skills**, not slash commands, so confirm with `/skills` and look for `speckit-constitution`, `speckit-specify`, `speckit-plan`, `speckit-tasks` and `speckit-implement`. Three optional ones come with it: `speckit-clarify`, `speckit-analyze` and `speckit-checklist`.

## Part A: Lock the Principles

Each command feeds the next, so do not skip steps: every one narrows scope before the next expands it.

```text
/speckit-constitution Principles: 1. Python stdlib only beyond Typer. 2. Storage is SQLite via sqlite3, no ORM. 3. Every command must be testable in isolation. 4. Existing notes.db rows survive all schema changes. 5. CLI surface stays small: at most two new commands per feature.
```

Expected result: a constitution file the later steps read. Principle 4 is the one to watch; it is what should make the plan step choose an idempotent migration on its own.

## Part B: Specify, Plan, Tasks

The split between these three is the whole point: `specify` stays user-facing and says nothing about schema, `plan` adds the technical decisions, `tasks` turns the plan into ordered units.

```text
/speckit-specify Add tag-based search and pinning to notes-cli. Users attach tags to notes, search with AND semantics across multiple tags, and mark notes pinned so they sort first. Existing notes without tags or pins work unchanged.
```

```text
/speckit-plan Tech stack: Python 3.12, Typer, sqlite3 stdlib. Tags: normalised table plus junction table, no JSON columns. Pinned: integer column on notes (default 0). Multi-tag query: GROUP BY note_id HAVING COUNT(DISTINCT tag_id) = N. List order: pinned DESC, id DESC. Migration runs idempotently on startup.
```

```text
/speckit-tasks
```

Read `specs/<feature>/spec.md` before running the last step. It should be silent on tables and columns; if schema decisions leaked into the spec, that is the failure this pipeline exists to prevent.

## Part C: Implement and Compare

```text
/speckit-implement
```

Expected result: the task list executes and the artefacts update as each task completes. Then hold the output against your hand-driven planning from [02: Extended Thinking and Statefiles](../02-extended-thinking/readme.md):

```text
Compare specs/<feature>/spec.md against the STATE.md I wrote by hand. Answer three questions:
  1. Which document is more verbose, and which audience is each written for?
  2. Where did the schema decisions end up in each approach?
  3. Which one would survive being handed to someone who has never seen this project?
```

Spec Kit's spec is more verbose, more user-facing, and silent on schema; those choices arrive in `plan.md`. That separation is the difference from a single STATE.md that carries everything at once.

The finished feature this pipeline describes is checked in at [notes-cli-solution/](notes-cli-solution/); use it to check what your run produced, not as a substitute for running it.

## Helpful Spec Kit Skills

Each one is invoked the same way a slash command is, but it is a skill under `.claude/skills/` that `specify init` installed.

| Skill | Usage |
|---|---|
| `/speckit-constitution` | Lock governing principles before any feature work (requires the `specify` CLI) |
| `/speckit-specify` | Produce a feature spec from a product-level description |
| `/speckit-plan` | Add technical choices and architecture decisions on top of the spec |
| `/speckit-tasks` | Decompose the plan into an ordered, numbered task list |
| `/speckit-implement` | Execute the task list and update artefacts as each task completes |
| `/speckit-clarify` | Optional: ask structured questions to de-risk ambiguity, run before `/speckit-plan` |
| `/speckit-analyze` | Optional: cross-artefact consistency report, run after `/speckit-tasks` |

## Key Topics Covered in This Demo

- [Spec Kit on GitHub](https://github.com/github/spec-kit): source, README, and skill definitions
- [Claude Code memory (CLAUDE.md)](https://code.claude.com/docs/en/memory): where constitution principles live once you want them in every session
