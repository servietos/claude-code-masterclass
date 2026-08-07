# Build Custom Slash Commands

## What Are Slash Commands?

Slash commands are reusable, named workflows stored as Markdown files in `.claude/commands/`. Typing `/command-name` in Claude Code loads the file as an injected prompt and executes it with full access to the current session context. They turn long, multi-step instructions into a single invocation.

The core benefit is eliminating repetition. Any task you perform more than twice is a candidate for a slash command: generating boilerplate, running a review cycle, or scaffolding documentation. Once written, the command is available to every teammate who checks out the repo, with no setup required beyond the file existing in `.claude/commands/`.

Slash commands accept arguments via the `$ARGUMENTS` placeholder, which is replaced at invocation time with whatever the user types after the command name. This makes them composable: the same command can target different modules, files, or lab numbers depending on what is passed.

## How This Repo Uses Slash Commands

This masterclass repository relies on three custom slash commands to produce all of its demo and lab content. Instead of crafting lengthy prompts by hand for each new module, the author invokes a command and passes minimal arguments: the rest of the structure, conventions, and output format are encoded in the command file itself.

The table below lists all three commands, their locations, and what they do:

| Command | File | Purpose |
|---------|------|---------|
| `/scaffold-teaching-subfolders` | `.claude/commands/scaffold-teaching-subfolders.md` | Creates the standard folder tree for a new module: numbered subfolders, `readme.md`, and a `pptx/` subfolder inside each. |
| `/create-teaching` | `.claude/commands/create-teaching.md` | Reads source files in a module folder and rewrites or enhances its `readme.md` with what the module covers, a slash command table, and documentation links. |
| `/create-lab` | `.claude/commands/create-lab.md` | Scaffolds a new lab file under `labs/` in either guided (step-by-step) or prompt-based (Goal / Prompt / Expected result) format. |

Every readme in this repo was produced or enhanced by `/create-teaching`. Every lab file was scaffolded by `/create-lab`. The folder structure you are reading now was created by `/scaffold-teaching-subfolders`.

```text
/scaffold-teaching-subfolders demos/02-harness

Intro
Commands
MCP
```

```text
/create-teaching in demos/02-harness/02-commands/readme.md describe slash commands and their benefits
```

```text
/create-lab module=02 number=01 title="Custom Slash Commands" type=prompt-based
```

## Anatomy of a Slash Command File

A command file is a plain Markdown document. The filename (without `.md`) becomes the command name. The `$ARGUMENTS` token is replaced at runtime with any text the user types after the command name.

```markdown
# My Command

$ARGUMENTS

Do the following with the argument above:
1. Read the file at the given path.
2. Summarize its purpose in three sentences.
3. Suggest one improvement.
```

Saved to `.claude/commands/my-command.md`, this becomes `/my-command path/to/file.ts`. Command files can be as simple as a few lines or as detailed as multi-section workflow definitions with rules, output structure requirements, and example invocations.

## Beyond Content Generation

Slash commands apply equally well to engineering workflows outside of documentation. The pattern is the same: encode a repeatable sequence of steps, give it a name, and invoke it with context-specific arguments.

| Use Case | Example Command | What It Does |
|----------|-----------------|--------------|
| Testing | `/run-tests` | Runs the test suite, captures failures, and opens each failing file for inspection. |
| Code review | `/review` | Diffs the current branch against main, checks for common issues, and produces a structured review. |
| Security | `/security-review` | Audits changed files for OWASP top-10 patterns and reports findings with line references. |
| Documentation | `/update-docs` | Reads a changed module and rewrites its corresponding `docs/` entry to match. |
| Database | `/run-migrations` | Runs pending migrations, verifies the schema, and rolls back automatically on failure. |
| CI debug | `/fix-ci` | Fetches the latest CI log, identifies the failing step, and attempts an automated fix. |
| Release | `/create-pr` | Generates a pull request description from commits since the last merge and opens a draft PR. |
| Onboarding | `/setup-env` | Walks a new developer through environment setup with OS-specific tracks. |

The `/review` and `/security-review` commands shown in the table above are installed globally in this masterclass setup and available in every session. They demonstrate the second scope for slash commands: `~/.claude/commands/` for personal or cross-project workflows that should not be committed to any specific repository.

## Built-in Slash Commands

Claude Code ships with several built-in commands alongside any custom ones. These cannot be overridden but are available in every session without any configuration.

| Command | Purpose |
|---------|---------|
| `/help` | Show available commands and keyboard shortcuts. |
| `/clear` | Clear the conversation context and start fresh. |
| `/config` | Open the interactive settings panel. |
| `/cost` | Display token usage and estimated cost for the current session. |
| `/doctor` | Run a health check on the Claude Code installation. |
| `/init` | Generate a `CLAUDE.md` for the current project. |
| `/memory` | Open the global `CLAUDE.md` for editing. |
| `/model` | Switch the active model mid-session. |
| `/vim` | Toggle vim keybindings. |

## Hands-On Demo

[Automate a Release CLI with Custom Slash Commands](demo-slash-command-toolkit.md) turns a dependency-free changelog CLI into a four-command toolkit, covering frontmatter fields, positional arguments, the `` !`command` `` bash injection, and project versus personal scope. The pristine starter is `command-toolkit/`; the finished reference is `command-toolkit-solution/`.

## Helpful Claude Slash Commands

| Command | Usage |
|---------|-------|
| `/review` | Run a structured code review of the current branch, a prime example of a team slash command. |
| `/security-review` | Audit all changes on the current branch for security issues before merging. |
| `/cost` | Display token usage and estimated cost for the current session. |
| `/help` | List all available commands (built-in and custom) and keyboard shortcuts. |

## Key Topics covered in this module

- [Slash Commands Reference](https://code.claude.com/docs/en/slash-commands): authoring custom commands, `$ARGUMENTS`, and scope resolution
- [Built-in Command Reference](https://code.claude.com/docs/en/commands): full list of built-in slash commands with descriptions
- [CLAUDE.md Memory](https://code.claude.com/docs/en/memory): how project context files are discovered and merged
- [Claude Code Settings](https://code.claude.com/docs/en/settings): where to place commands for global vs. project scope
- [Hooks](https://code.claude.com/docs/en/hooks): complement slash commands with event-driven automation
