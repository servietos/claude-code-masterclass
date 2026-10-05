# Module 1: Claude Code Fundamentals

- Claude product family and surfaces
- Installation, authentication, editor setup
- Model selection and token cost
- Prompt caching: prefix, invalidation, hit rate
- Permission tiers, modes, scope precedence
- Session checkpoints and rollback
- Git worktrees and the Agents View
- Publishing artifacts: versions and sharing

## Topics

| Topic | Description |
|-------|-------------|
| [01: Introduction](01-intro/readme.md) | The Claude product family (Claude.ai, Desktop, Code CLI, IDE extensions, API, and Managed Agents) and why the terminal-first tool is the focus of this course. |
| [02: Setup](02-setup/readme.md) | Installing Node.js and the `@anthropic-ai/claude-code` CLI, first-time authentication, and configuring the VS Code and Claude Terminal extensions. |
| [03: Editors](03-editors/readme.md) | Running Claude Code in the terminal, VS Code sidebar, and Claude Desktop, with guidance on which environment fits which working style. |
| [04: Model Selection](04-model-selection/readme.md) | Choosing between Opus, Sonnet, and Haiku based on task complexity, managing token usage and session cost, and keeping the prompt cache warm: how Claude Code orders each request into a system prompt, project context, and conversation layer, the actions that invalidate the cached prefix and the ones that safely append, why a mid-session `CLAUDE.md` edit is silently inert, the five-minute and one-hour TTLs, per-directory cache scope, and reading `cache read` against `cache write` in `/usage`. |
| [05: Permissions](05-permissions/readme.md) | The three permission tiers, the allow/ask/deny rule syntax, permission modes, and the settings scopes that decide which rule wins. |
| [06: Checkpoints and Worktrees](06-git-worktrees/readme.md) | Session checkpoints for undoing file changes, rolling back risky edits, and keeping long sessions safe; how git worktrees enable parallel branch checkouts, the `--worktree` flag and `EnterWorktree` tool that isolate agentic changes from your working copy, and how to clean them up. |
| [07: Agents View](07-agents-view/readme.md) | Dispatching background sessions with `--bg`, triaging the board by state, the keys that let you peek and reply without attaching, and the supervisor that keeps sessions alive. |
| [08: Artifacts](08-artifacts/readme.md) | Publishing session output as a live page on claude.ai: the permission prompt and `Ctrl+]`, versions and the sharing model, design tokens read from `CLAUDE.md`, the Content Security Policy constraints, and the availability rules that decide whether publishing works at all. |

## Demos

| Topic | Description |
|-------|-------------|
| [04: Model Selection](04-model-selection/demo-model-routing.md) | Runs the same tasks on Haiku, Sonnet, and Opus against one API, measures each with `/usage` and `/context`, and writes the measured routing policy into CLAUDE.md. |
| [04: Model Selection](04-model-selection/demo-cache-hit-rate.md) | Warms a cache across three turns on a dependency-free TypeScript sample, breaks it on purpose with a `/model` switch, proves a mid-session `CLAUDE.md` edit is inert until `/clear`, compares `/compact` against `/rewind`, and records every reading in `CACHE-NOTES.md`. |
| [05: Permissions](05-permissions/demo-permission-settings.md) | Builds `.claude/settings.json` with allow and deny rules, makes a secrets file unreachable by file and by shell, and splits team policy from a git-ignored personal override. |
| [06: Checkpoints and Worktrees](06-git-worktrees/demo-anchor-and-roll-back-a-session.md) | Anchors a green Node test suite, lets Claude run an over-reaching cross-cutting refactor, then rewinds and proves the rollback with `npm test` and a clean `git status`. |
| [06: Checkpoints and Worktrees](06-git-worktrees/demo-worktrees-intro.md) | Runs two Claude sessions in parallel worktrees editing the same file, then reviews, merges, and cleans up the branches they produce. |
| [07: Agents View](07-agents-view/demo-agents-view.md) | Dispatches three background sessions on independent chores, triages them from the board without attaching, reviews each branch in place, and merges only the work that earns it. |
| [08: Artifacts](08-artifacts/demo-artifact-publish-share.md) | Publishes a CI failure dashboard from a CSV, revises it in place through versions, restyles it from design tokens in `CLAUDE.md`, lays three remediation plans side by side with a copy-as-prompt control, and proves the fallback when `Artifact` is denied. |

Every demo has a presenter guide beside it (`demo-presenter-<slug>.md`) holding the same
teaching in timed beats, for delivery without running the demo live.

## Labs

| Lab | Description |
|-----|-------------|
| [Install and Set Up Claude Code](../../labs/01-fundamentals/01-setup-claude/readme.md) | Install the Claude Code CLI, authenticate, and explore it through the VS Code extension. |
| [Build a Task Tracking REST API](../../labs/01-fundamentals/02-hello-claude/readme.md) | Build a Python REST API for task management, every step driven by a prompt you write. |

## Knowledge Check

### CQ-01: Picking the Right Product

A platform team wants an assistant that reads their monorepo, edits a dozen files across two services, runs the test suite, inspects the failures, and opens a pull request, all driven from a terminal inside the project directory. Which product in the Claude family fits?

- A) Claude.ai, because the web chat accepts pasted file contents and returns corrected versions.
- B) Claude Desktop, because its MCP connections give it local file access and control over other apps.
- C) Claude Code CLI, because it runs where the code lives and can invoke shell commands and git.
- D) The Anthropic API directly, because multi-file work needs full control over the system prompt.

**Answer: C**

Claude Code is the only member of the family that combines persistent repository context, shell execution, and git awareness in one loop. Claude.ai and Claude Desktop are conversational and will not run the test suite and iterate on its failures. The API is the layer everything else is built on, so choosing it means rebuilding the agentic loop that already exists.

### CQ-02: What Invalidates the Cache

A developer edits `CLAUDE.md` mid-session to add a new coding rule, then continues working in the same conversation. Claude keeps ignoring the new rule. What is happening?

- A) The edit is silently inert; project context loaded at session start, and the new content applies only after `/clear`, `/compact`, or a restart.
- B) The rule was written below the cache breakpoint, so it loads but at a lower priority than the rules above it.
- C) `CLAUDE.md` edits require running `/memory` to flush the file back into the session.
- D) The file is re-read on every turn, so the rule is already active and the model is simply choosing not to follow it.

**Answer: A**

A mid-session `CLAUDE.md` edit does not reach the running session. Claude keeps working from the version loaded when the session started, and the new content arrives on the next `/clear`, `/compact`, or restart. Nested `CLAUDE.md` files in subdirectories behave differently, because they load later, when Claude first reads a matching file.

### CQ-03: Routing Work Across Models

A team runs three kinds of task through Claude Code: bulk mechanical edits across many files, everyday feature work, and one architectural review per sprint. They want to control cost without slowing the hard work down. What is the sound routing policy?

- A) Run everything on Opus, because a single model keeps behavior consistent and consistency is worth the cost.
- B) Run everything on Haiku and escalate manually whenever the output looks wrong.
- C) Route mechanical bulk work to Haiku, everyday feature work to Sonnet, and the architectural review to Opus.
- D) Route by file count: anything touching more than ten files goes to Opus regardless of task type.

**Answer: C**

Model selection tracks task complexity, not task size. Mechanical edits are cheap to verify and cheap to redo, so Haiku is the right default there; Sonnet carries ordinary feature work; Opus earns its cost on the reasoning-heavy review that happens once a sprint. Option D uses a proxy that does not correlate with difficulty, since a ten-file rename is easier than a one-file concurrency bug.

### CQ-04: Which Permission Rule Wins

A repo ships `.claude/settings.json` allowing `Bash(npm run test:*)`. A developer adds a personal `~/.claude/settings.json` that denies all `Bash`. The organization also ships a managed settings file that allows `Bash(npm run *)`. Which rule governs the session?

- A) The user-level deny, because deny always outranks allow regardless of scope.
- B) The project-level allow, because project settings are the most specific to the work being done.
- C) The managed settings, because that scope outranks project, user, and even command line arguments.
- D) None of them; conflicting rules across scopes cause Claude Code to fall back to prompting.

**Answer: C**

Managed settings are a fourth scope above local, project, and user settings, and they outrank command line arguments too. That precedence is exactly what makes them a security control rather than a suggestion. Deny-over-allow resolves conflicts *within* a scope, which is why option A is a real rule applied at the wrong level.

### CQ-05: Parallel Work Without Collisions

Two Claude Code sessions need to work on the same repository at once, on unrelated features that both touch `src/config.ts`. What keeps them from corrupting each other's work?

- A) Run both sessions in the same checkout but instruct each to edit only its own feature's files.
- B) Give each session its own git worktree, so each has an isolated checkout on its own branch.
- C) Run the second session with `--resume` against the first, so they share one conversation and cannot conflict.
- D) Run them sequentially; concurrent sessions on one repository are unsupported.

**Answer: B**

Git worktrees give each session an isolated working copy on its own branch, so simultaneous edits to the same path cannot collide and the merge happens deliberately at the end. Option A relies on instructions holding across two independent agents, which is exactly what fails. Option C would merge the two tasks into one context rather than isolating them.

### CCA-F Q26 (Domain 2: Tool Design and MCP Integration)

A security patch requires changing the signature of the `verifyToken(token)` function to `verifyToken(token, options)`. The function is used extensively across a large monolithic backend. What is the most efficient way to locate every file that needs to be updated?

- A) Use the Bash tool to run the test suite and only modify the files that throw compilation errors regarding verifyToken.
- B) Use the Edit tool with a wildcard pattern verifyToken(*) to automatically update all signatures in one pass.
- C) Use Grep with the pattern verifyToken( to search the file contents and identify all caller files and their contexts.
- D) Use Glob to find all .js and .ts files, then Read each one sequentially to check for the function invocation.

**Answer: C**

Grep is the most efficient tool for searching file contents directly. It is designed for pattern-matching tasks and can quickly scan through a large codebase to locate call sites, providing line numbers and context for the required updates.

### CCA-F Q33 (Domain 2: Tool Design and MCP Integration)

A developer is working on a large frontend monorepo that consumes various backend APIs. They need to deprecate a specific REST endpoint, `/api/v1/inventory`, which is used across the codebase. The endpoint path is sometimes constructed dynamically (e.g., `const path = '/api/v1' + '/inventory'`). According to Anthropic's official documentation and recommended practices, what is the most reliable and comprehensive method to find all usages of this endpoint before removing it?

- A) Refactor the code to centralize all API endpoint definitions into a single configuration file, then search that file.
- B) Use Claude Code to analyze the codebase and identify all usages of the endpoint, including dynamically constructed paths.
- C) Use `grep` to search the entire codebase for the literal string `/api/v1/inventory`.
- D) Manually inspect the browser's Network tab while clicking through every part of the application to see if the endpoint is called.

**Answer: B**

Anthropic's official documentation highlights Claude Code as a tool for complex code analysis and migration. Claude Code can understand code structure and semantics, making it capable of identifying both literal and dynamically constructed API endpoint usages.

### CCA-F Q36 (Domain 2: Tool Design and MCP Integration)

You need to completely replace the contents of a legacy `webpack.config.js` file with a brand new, standardized 20-line configuration provided by the platform team. The old file contains 300 lines of outdated custom plugins. Which tool application is most appropriate?

- A) Use the Write tool directly to overwrite the entire `webpack.config.js` file with the new 20-line configuration.
- B) Use the Edit tool, matching the first and last lines of the old file, and replacing the entire block with the new configuration.
- C) Use the Grep tool to delete the old contents line-by-line, then use the Write tool to insert the new configuration.
- D) Use the Bash tool to `rm` the file, then use the Edit tool to create a new file with the same name.

**Answer: A**

The Write tool is the most efficient and direct method for this task because it is designed to atomically create or overwrite a file's entire content. It ensures a clean replacement without the complexity of pattern matching or multi-step operations.

### CCA-F Q42 (Domain 2: Tool Design and MCP Integration)

You need to append a new utility function `export const validateEmail = (email) => { ... }` to the very end of a 3,000-line `validators.ts` file. You want to accomplish this with the least amount of token overhead. Which approach is optimal?

- A) Use the Read tool to load the entire validators.ts file, append the validateEmail function in memory, and then use the Write tool to save the complete updated file.
- B) Use the Edit tool, matching the last few lines of the file as the anchor text, and replacing them with those same lines followed by the new function.
- C) Use the Write tool to overwrite validators.ts with only the new validateEmail function, which replaces the entire 3,000-line file and discards all existing validation logic.
- D) Use the Grep tool to locate the end-of-file marker in validators.ts, then pipe the validateEmail function into the file by appending it after the marker.

**Answer: B**

The Edit tool allows surgical modifications by matching a small anchor (the last few lines) and replacing them with the same lines plus the new function. This minimizes token usage because only the anchor and replacement text need to be processed, not the entire file.
