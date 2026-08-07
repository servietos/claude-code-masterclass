# Apply Prompting Techniques

Apply five prompting techniques to a real project's harness: statefile maintenance, anchors, `@`-mentions, few-shot examples, and slash-command promotion.

Each step contains:

- **Goal**: what you are building
- **Prompt**: paste this into Claude Code
- **Expected result**: what the outcome looks like

Work in [`03-prompting/users-api/`](03-prompting/users-api/readme.md); the finished result is beside it in [`03-prompting/users-api-solution/`](03-prompting/users-api-solution/readme.md). Build your own version first, then diff against it.

---

## Where to Open Claude Code

This lab builds its own harness, so open Claude Code inside the lab project rather than at the repo root. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves everything you write here inert, with no error to tell you.

The starter is already in this repo, so there is nothing to scaffold: change into it and start the session there. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/01-fundamentals/03-prompting/users-api
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `users-api` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the commands above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere in the repo:

```text
In labs/01-fundamentals/03-prompting/users-api add a DELETE /users/:id endpoint to api/index.ts ....
```

That works for any step whose result is just files. It does not work for the harness steps: `CLAUDE.md`, `.claude/commands/state-tick.md` and `.claude/settings.json` load from the directory the session was launched in, so a root session writes them into the lab folder and then ignores them. Launch inside `users-api` from Step 1 onward.

Restart the session with `/exit` then `claude` after any edit to `.claude/settings.json`, because settings are read at startup.

Launching inside the starter is what makes the repository a monorepo to this lab rather than the project: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session. You read them from the repo root without ever writing into them, and every path in the prompts below is relative to the lab folder.

---

## Setup: Run the Starter

Everything in this lab happens inside one small TypeScript API, the starter you just opened in `users-api`. It already ships the file layout every later step depends on: `api/index.ts` holds the `buildApp(seed)` factory, the `seedUsers(count)` helper and the `GET /users` and `POST /users` routes, `api/index.test.ts` holds the Vitest suite, and `api/server.ts` holds nothing but the listen call. Steps 3 and 4 `@`-mention those two paths, so nothing here asks you to create them.

Install and prove the starter is green before you touch it:

```bash
npm install
npx tsc --noEmit
npx vitest run
```

**Expected result:** `npm install` reports `added 100 packages, and audited 101 packages`, `found 0 vulnerabilities`. `npx tsc --noEmit` prints nothing and exits 0. `npx vitest run` reports `Test Files 1 passed (1)` and `Tests 4 passed (4)` against the starter's GET and POST cases.

One ESM detail the starter already reflects: `"type": "module"` plus `moduleResolution: NodeNext` means relative imports keep the `.js` extension (`import { buildApp } from "./index.js"`) even though the file on disk is `index.ts`. Dropping the extension in the code you add fails the type-check with `error TS2835: Relative import paths need explicit file extensions ... Did you mean './index.js'?`.

Now create the harness file the next two steps operate on:

```text
Create CLAUDE.md at the project root with these sections and one short paragraph in each:

  ## Architecture
  ### File Layout
  ### Module Boundaries
  ## Conventions
  ### Error Handling
  ### Naming
  ## Testing
  ### Test Style

Describe what this project actually does: the buildApp(seed) factory, Zod safeParse with 400 and a snake_case error code, 404 with {"error": "not_found"}, Vitest with app.inject() and it.each tables, no fixture files.
```

**Expected result:** A `CLAUDE.md` with those eight headings, each describing a rule the code already follows. Steps 1 and 2 both edit this file, so it has to exist before you continue.

---

## Step 1: Statefile Maintenance

**Goal:** Create a `STATE.md` and establish the habit of updating it every session so any future Claude run can resume without re-asking.

**Prompt:**

```text
Create STATE.md at the project root with this exact section structure:

  # API Project State

  ## Goal
  [one sentence: what this project is]

  ## Decisions
  [bullet list of locked-in choices: Fastify, Zod, ESM, NodeNext, buildApp factory]

  ## Status
  - [x] Initial scaffold
  - [ ] DELETE /users/:id endpoint
  - [ ] Pagination on GET /users
  - [ ] Soft-delete migration

  ## Next Action
  [the single next concrete thing to do]

  ## Open Questions
  [empty bullet list]

Then add a rule at the top of CLAUDE.md:
  "Read STATE.md before any non-trivial change. Update STATE.md after any non-trivial change."

Confirm both files exist and the rule is in CLAUDE.md.
```

**Expected result:** A `STATE.md` with all five sections filled in, three unchecked boxes under Status, and a Next Action line naming the DELETE endpoint. `CLAUDE.md` gains the read-and-update rule as its first line under the title. From here on, every meaningful change to the project walks through `STATE.md`.

---

## Step 2: Anchors

**Goal:** Add stable section IDs to `CLAUDE.md` so prompts can reference rules by anchor (`see §arch-2`) instead of re-pasting paragraphs.

**Prompt:**

```text
Refactor CLAUDE.md to add anchor IDs to every section heading. Use the form:

  ## Architecture {#arch}
  ### File Layout {#arch-1}
  ### Module Boundaries {#arch-2}
  ## Conventions {#conv}
  ### Error Handling {#conv-1}
  ### Naming {#conv-2}
  ## Testing {#test}
  ### Test Style {#test-1}

The anchor format is `{#short-id}` immediately after the heading text. Anchors are short, stable, and hyphenated. Numbering is parent-child where useful.

Then add a rule to CLAUDE.md: "When you cite a rule from this file, cite it as `see §<anchor-id>`."
```

**Expected result:** All eight headings in `CLAUDE.md` now carry an anchor, and the citation rule sits next to the STATE rule at the top of the file. Ask Claude anything that touches a convention and it answers with "per §conv-1 ..." instead of pasting the rule back at you. Rule conflicts get much easier to diagnose once every rule has an address.

---

## Step 3: `@`-Mention Discipline

**Goal:** Replace pasted code with `@path/to/file.ts` references so the harness pulls fresh content on every turn instead of using stale snapshots from earlier in the conversation.

**Prompt:**

```text
Add a DELETE /users/:id endpoint to @api/index.ts.

Constraints:
  - Match the validation pattern in @api/index.ts (Zod safeParse, snake_case error codes).
  - Match the test pattern in @api/index.test.ts (it.each, app.inject(), no fixtures).
  - A missing id returns 404 with {"error": "not_found"}.
  - Update STATE.md Status: flip the DELETE checkbox.

Do not paste any code into this prompt. Use only @-mentions for file references.
```

**Expected result:** Claude reads both files fresh, infers the patterns, and adds the endpoint plus its tests. `npx tsc --noEmit` stays clean and `npx vitest run` stays green with the new cases. Against a running server the behaviour is `DELETE /users/2` returning `204` with an empty body, and `DELETE /users/99` returning `{"error":"not_found"}`. `STATE.md` shows DELETE as `[x]`, and the transcript contains file references only, no pasted code.

After it finishes, ask:

```text
Compare this turn against a hypothetical turn where I pasted the full contents of @api/index.ts and @api/index.test.ts into the prompt. Where does the @-mention actually save context, and where does it save nothing?
```

The saving is not in the first turn: the file content gets loaded either way, and in this project that is only about 5.8 KB across both files. The saving is in every turn after it, because the mention re-reads the file as it is now instead of forcing you to re-paste, and it never leaves a stale copy of the code sitting in the transcript. Check the estimate Claude gives against the real file sizes; the numbers models guess here are usually too high.

---

## Step 4: Few-Shot Examples

**Goal:** Anchor consistency on a recurring task by including two or three input/output examples in the prompt. Useful when the model's first attempt drifts in style or format.

**Prompt:**

```text
I want to add pagination to GET /users. Here are two examples of how pagination response shapes look in this codebase:

Example 1, endpoint GET /products?page=2&size=20
Response:
{
  "data": [...],
  "page": 2,
  "size": 20,
  "total": 87,
  "has_next": true
}

Example 2, endpoint GET /orders?page=1&size=10
Response:
{
  "data": [...],
  "page": 1,
  "size": 10,
  "total": 3,
  "has_next": false
}

Apply this exact shape to GET /users in @api/index.ts. Reject page < 1 and non-numeric size with 400 and error code invalid_query.

In @api/index.test.ts:
  - Add an it.each test covering page=1, page=2 and page=3 against buildApp(seedUsers(25)).
  - Also update the existing GET /users test: the endpoint now returns the envelope, not a bare array.

Do not touch STATE.md in this step.
```

**Expected result:** The `/users` response matches the two examples field for field, and `npx vitest run` reports `Test Files 1 passed (1)`, `Tests 12 passed (12)`. The reminder about the existing test is what keeps the suite green: leave it out and the old assertion fails with `expected { data: [], page: 1, size: 20, ...(2) } to deeply equal []`, because the shape changed underneath it. Against a running server with three users, `GET /users?page=1&size=2` returns `"total":3,"has_next":true`, `page=2` returns `has_next:false`, and `GET /users?page=0` returns `400`. Without the few-shot, Claude would plausibly have invented `cursor` or `next_url`; with two examples in front of it the shape stays stable across teammates and future sessions.

---

## Step 5: Slash-Command Promotion

**Goal:** Take a prompt you have now typed three times and promote it to a project slash command so it becomes one keystroke.

**Prompt:**

```text
Every step in this lab has updated STATE.md: flip a checkbox, rewrite the Next Action line. That is a repeated motion.

Promote it to a project slash command. Create .claude/commands/state-tick.md in this project,
the users-api folder you launched the session in, with content:

  ---
  description: Update STATE.md after finishing a task, flips the matching checkbox and rewrites the Next Action line based on the remaining unchecked items.
  ---

  Read @STATE.md. The user just finished a task, they will tell you which Status checkbox to flip (or you can infer from the last few messages). Flip the matching `[ ]` to `[x]`. Then rewrite the "Next Action" section based on the highest-priority remaining unchecked item.

  Save the file and confirm with a one-line summary of what changed.

Then test it: type /state-tick and ask it to flip the "Pagination on GET /users" checkbox.
```

**Expected result:** A `.claude/commands/state-tick.md` with YAML frontmatter carrying a `description` field, which is what makes the command show up in the `/` menu. Because Step 4 deliberately left `STATE.md` alone, the pagination box is still `[ ]` and the command has real work to do. After `/state-tick`, Status reads `- [x] Pagination on GET /users` and Next Action points at the soft-delete migration, the only unchecked item left. The four-line manual edit you did by hand three times is now one command.

---

## Step 6: Fewer Permission Prompts

**Goal:** Stop approving the same handful of commands over and over by writing them into a project allowlist.

By now you have approved `npm install`, `npx tsc --noEmit` and `npx vitest run` several times each. Claude Code asks before every Bash call and every write it has not been cleared for, and the approval you give in the prompt box lasts only for that session. A `permissions.allow` entry in the project's settings makes the decision once and keeps it: the tool runs silently, everything not on the list still stops and asks.

**Prompt:**

```text
Create .claude/settings.json in this project with a permissions.allow list covering the
commands this lab actually runs: npm, npx, and reading files under this folder.

Use prefix matching, for example Bash(npm:*), so npm install and npm run test are both
covered by one entry. Do not add anything I have not run.
```

The result should look like this:

```json
{
  "permissions": {
    "allow": ["Bash(npm:*)", "Bash(npx:*)", "Bash(ls:*)", "Read(./**)"]
  }
}
```

Settings are read at startup, so restart with `/exit` then `claude` before testing. Then run `npx vitest run` again: it executes with no prompt.

**Expected result:** A `.claude/settings.json` carrying the four allow entries, and a session where the test and type-check commands stop interrupting you while anything outside the list (a `rm`, a `git push`, a write outside the project) still asks.

Three details worth knowing:

- `/permissions` opens the same list in the UI, and the "Yes, and don't ask again" option on any approval dialog appends to it for you. Both write to `.claude/settings.local.json`, which is git-ignored and personal to you; `.claude/settings.json` is the shared, committed version for a team.
- `Shift+Tab` cycles the session's permission mode. `accept edits on` stops the prompts for file writes without touching the allowlist, and it resets when the session ends. Reach for it when you are supervising a long edit run, not as a permanent setting.
- The `/fewer-permission-prompts` command does this step automatically: it reads your own transcripts, finds the calls you keep approving, and proposes the allowlist entries for them.

The thing to resist is `claude --dangerously-skip-permissions`, which approves everything for the whole session. An allowlist is the same convenience with a boundary still in place: you decided in advance which commands are safe here, and this file scopes that decision to this project.

---

## What You Just Practised

| Technique                  | Step | When to reach for it                                                                                    |
| -------------------------- | ---- | ------------------------------------------------------------------------------------------------------- |
| Statefile maintenance      | 1    | Every project, every session: the cheapest single discipline you can adopt                              |
| Anchors / section IDs      | 2    | Once `CLAUDE.md` exceeds roughly 50 rules, citation becomes painful without them                        |
| `@`-mentions over pasting  | 3    | Every multi-turn session where files change mid-conversation                                            |
| Few-shot examples          | 4    | Any recurring task with a stable output shape: pagination, log lines, commit messages                   |
| Slash-command promotion    | 5    | Any prompt you have typed 3+ times                                                                      |
| Permission allowlist       | 6    | Any project where you approve the same build, test or lint command more than twice                      |
