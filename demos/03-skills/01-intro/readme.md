# What Is a Skill?

A skill is a Markdown file with YAML frontmatter stored in a named subdirectory under `.claude/skills/`. Claude reads the `description` field of every installed skill and uses it to detect when the user's message matches. Claude Code watches the skill directories, so a skill you add or edit takes effect within the current session; only creating a skills directory that did not exist when the session started requires a restart. Describing what you need is enough for Claude to load the matching skill on its own, and typing `/<directory-name>` invokes it explicitly when you want to be certain it fires.

Skills are the right choice when a workflow is reusable across projects or teams, when it needs companion files (rules documents, configuration JSON, shell scripts), or when it should delegate to reference documents it loads on demand. The discoverability comes at the cost of precision: because matching is semantic, a vague description can cause false triggers.

Semantic matching is invisible, so the transcript is where you confirm it happened. A loaded skill prints one line naming the directory it came from:

```text
● Skill(brand-voice-code)
  Successfully loaded skill
```

Absence of that line is the answer when a skill seems not to have applied: the `description` did not match, and no amount of rewording the request fixes a description that never mentions the phrasing users actually type.

## Understand Skills vs Slash Commands

Skills and slash commands are both ways to extend Claude Code with custom behaviors, and the two have converged: a file under `.claude/commands/` and a `SKILL.md` under `.claude/skills/` both produce a `/name` command and accept the same frontmatter. What still separates them is packaging. Invocation feels like a second difference, and getting that wrong is how people reach for the wrong tool.

## What Actually Separates Them

A skill is a folder; a slash command is a single file. That is the entire structural difference: a skill can ship reference documents, scripts, and templates beside its instructions and load them only when they are needed, while everything a command does has to fit inside its one file. So the choice is a packaging choice, and nothing more: a skill when there is something to bundle, a flat command when the procedure is self-contained.

Do not pick the folder in order to control triggering. Two frontmatter fields control that, and they behave the same in both folders: `description` decides how readily Claude matches the file on its own, and `disable-model-invocation: true` switches that matching off. A command with a broad description fires without being typed, and a skill with no description never fires at all.

The consequence worth knowing is arguments. A file Claude triggers on its own receives no argument string, so `$ARGUMENTS` and `$0` are empty; only typing `/deploy staging` fills them. Anything useless without typed arguments should set `disable-model-invocation: true`.

## Side-by-Side Comparison

| Dimension          | Skill                                                                                                     | Slash Command                                                                    |
| ------------------ | --------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Location           | `.claude/skills/<name>/SKILL.md`                                                                          | `.claude/commands/<name>.md`                                                     |
| Invocation         | Automatic on a `description` match, or explicit `/<directory-name>`                                       | Explicit `/<file-name> args`, or automatic when the file carries a `description` |
| Frontmatter        | YAML: `description` recommended, plus optional `name`, `allowed-tools`, `model`, `context`                | The same fields, all optional                                                    |
| Arguments          | `$ARGUMENTS`, positional `$0` and `$1`, or names declared in `arguments`                                  | The same substitutions                                                           |
| Tool access        | Optional `allowed-tools:` allowlist                                                                       | The same optional `allowed-tools:` allowlist                                     |
| Composition        | References and assets in subdirectories; further skills live in their own `.claude/skills/<name>/` folder | Flat; no nesting                                                                 |
| Multi-file support | Yes: scripts, JSON config, reference docs                                                                 | No: one file, nothing to bundle                                                  |
| Best for           | Reusable cross-project workflows that ship supporting files                                               | One-file project-specific procedural scripts                                     |

## Call a Skill from a Short Command

The two combine well. A skill holds the know-how, but calling it well still takes a paragraph: which skill, which folder, which style, which checks afterwards. A command can carry that paragraph once, with named arguments where the parts change, so the call you type shrinks to a name and three values.

```markdown
---
description: Write a demo guide for one topic of a module
argument-hint: [module] [topic] [title]
arguments: [module, topic, title]
disable-model-invocation: true
---

Use the create-class skill to write a demo guide for demos/$module/$topic, titled "$title".

- Read the topic readme first and teach what it teaches, concept first
- Prompt-recipe style: copy-paste inputs and an Expected Outcome after every step
- Save it as demos/$module/$topic/demo-<slug>.md and never overwrite an existing file
- Run the brand-voice-code skill on the result
```

Saved as `.claude/commands/new-demo.md`, it turns this line into the full prompt above, with every `$name` filled in from the arguments in order:

```text
/new-demo 03-skills 01-intro "Call a skill from a command"
```

Wrap a multi-word value in quotes to pass it as one argument. `argument-hint` shows the expected arguments in the `/` menu, and `disable-model-invocation: true` keeps Claude from running the command on its own, where the arguments would be empty. The expanded prompt names the skill, so Claude loads `create-class` with everything it needs on the first turn.

## Skill Anatomy

Every skill file opens with a YAML frontmatter block followed by a Markdown body.

```yaml
---
name: brand-voice
description: Audit and fix Markdown files for brand-voice quality: em dashes,
  Mermaid label syntax, paragraph length, and topic-specific slash command tables.
  Trigger phrases: "brand voice check", "quality check", "fix em dashes".
license: MIT
allowed-tools:
  - Read
  - Edit
  - Glob
  - Grep
---
```

Frontmatter fields:

| Field           | Required    | Purpose                                                                                                                                                                             |
| --------------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`          | No          | Display name shown in skill listings. Defaults to the directory name; in a project or personal skill the `/command` you type always comes from the directory, never from this field |
| `description`   | Recommended | Trigger text: include natural-language phrases, not just a definition. Defaults to the first paragraph of the body, which makes triggering unreliable                               |
| `license`       | No          | Metadata for publishing and sourcing from skill repositories                                                                                                                        |
| `allowed-tools` | No          | Tools the skill may use without a permission prompt during the turn that invokes it; accepts a space- or comma-separated string or a YAML list                                      |

The full field set is larger: `disable-model-invocation`, `argument-hint`, `arguments`, `disallowed-tools`, `model`, `effort`, `context`, `paths`, and `hooks` are all documented in the frontmatter reference linked at the end of this page.

The `description` field drives discoverability. Write it the way a user would ask for the skill, including example trigger phrases, so Claude matches correctly. A description that reads like a dictionary definition is harder to match than one that includes realistic user phrasings.

The `allowed-tools` list is a pre-approval, not a sandbox. Listing `Read`, `Glob`, and `Grep` means those three run without prompting for the turn that invokes the skill; every other tool stays callable and simply follows your normal permission flow. To actually take a tool away while the skill is active, list it in `disallowed-tools` instead.

## Skill Body Structure

Below the frontmatter, the body follows a consistent three-part layout:

```markdown
## Inputs

What the user must provide before the skill can run. If nothing is given,
describe what to ask for.

## Steps

Numbered procedure Claude follows to complete the task.

1. Read the configuration file.
2. Resolve the target path.
3. Apply the transformation.
4. Report the result.

## Output Format

How the result should be presented: tables, summaries, file diffs, etc.
```

Supporting sections (troubleshooting tables, rule references, architecture notes) go after the core three. The body is Claude's instruction set for this skill, written in the imperative, scoped to one responsibility, and free of prose comments or explanatory asides.

## Popular Skill Repositories

Skills are shared as Git repositories or zip archives. The table lists the most widely used sources.

| Repository / Source | Distribution Point | Install Method |
|---------------------|--------------------|----------------|
| [anthropics/skills](https://github.com/anthropics/skills) | GitHub | Copy the skill folder into `.claude/skills/` |
| Anthropic Skills Catalog (claude.ai) | Claude.ai web UI → Skills tab | One-click install from the catalog |
| [skills.sh](https://skills.sh) | Open agent skills directory (Vercel, open source) | `npx skills add <owner>/<repo>@<skill-name>` |
| [obra/superpowers](https://github.com/obra/superpowers) | Claude Code plugin marketplace | `/plugin install superpowers@claude-plugins-official` |
| [azure-samples/claude-skills-azure](https://github.com/Azure-Samples) | GitHub | Copy the skill folder into `.claude/skills/` |
| Team / private repo | Self-hosted Git (HTTPS or SSH) | Copy the skill folder into `.claude/skills/` |
| Local folder | Filesystem | Copy the skill folder into `.claude/skills/` |

To discover available skills from within a session, use the `/find-skills` command, which queries the catalog and presents matching results with install instructions.

```text
/find-skills Azure deployment
```

```text
/find-skills security review
```

## What an Install Changes

Installing a skill drops a folder and changes nothing else: no `settings.json` entry and no `CLAUDE.md` edit. Deleting that directory is the entire uninstall. The file must be named `SKILL.md` with that exact case, because a lowercase `skill.md` is not discovered on Linux or in CI and fails where you cannot see it.

## Hands-On Demo

[Use a DOCX Skill to create an Invoice Generator](demo-docx-invoice.md) searches the catalog for a DOCX skill, installs it, reads back the `SKILL.md` that landed on disk, and then lets the skill drive a TypeScript program that renders a sample invoice as a `.docx` file.

## Helpful Claude Slash Commands

| Command        | Usage                                                                   |
| -------------- | ----------------------------------------------------------------------- |
| `/find-skills` | Browse installed skills to see real frontmatter and body examples       |
| `/permissions` | Inspect which tools are currently allowed or blocked in your project    |
| `/mcp`         | List connected MCP servers: relevant when writing `mcp-server` metadata |

## Key Topics Covered in This Module

- [Claude Code Skills documentation](https://code.claude.com/docs/en/skills): official reference for skill frontmatter fields and directory layout
- [Claude Code Slash Commands documentation](https://code.claude.com/docs/en/slash-commands): built-in and custom slash command reference
- [Claude Code Settings and Permissions](https://code.claude.com/docs/en/settings): the project-level permission rules that still govern every tool a skill's `allowed-tools` does not pre-approve
