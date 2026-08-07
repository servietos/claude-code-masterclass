# Create a Skill from Scratch

Two paths lead to a working skill: writing it by hand, or extracting a workflow that already proved itself in a conversation. Both produce the same artifact, a directory with a `SKILL.md` file containing YAML frontmatter and Markdown instructions. Choosing between them depends on how clearly you already understand the workflow you want to encode.

This topic covers the file itself: where it goes, every frontmatter field, and how the body is structured. [03 Composite](../03-composite/readme.md) covers bundling scripts and reference files alongside it, [04 Live Data and Subagents](../04-live-data-and-subagents/readme.md) covers injecting live data and forking into a subagent.

## Start From a Failure Mode

The question that produces a useful skill is not which skill sounds useful. It is which failure you keep paying for. Agents fail in a small number of predictable ways, and each one has a different skill shape as its fix.

| Failure you keep hitting                                            | What it actually is                                    | The skill that fixes it                                                                     |
| --------------------------------------------------------------------- | -------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Claude built something other than what you meant                    | Alignment was never reached before code started        | An interview skill: ask about every branch of the plan, and write nothing until you agree   |
| Claude restates your own domain back to you in ten words per concept | Your project vocabulary is rediscovered every session  | A glossary skill: one shared-language file the skill reads before it names anything          |
| The code reads fine and breaks at runtime                           | Nothing gave Claude a signal about whether its output runs | A feedback-loop skill: the failing test comes first, as a gate rather than a suggestion   |
| The codebase drifts into many thin, tangled files                   | Each change landed without regard for the whole        | An architecture skill run on a schedule, looking for modules to deepen                       |

Write the one you can name from last week. A skill written for a failure you have not felt yet is also a skill whose `description` you cannot fill honestly, because you have never phrased the request that should trigger it.

## Manual Creation

Each skill is a directory with `SKILL.md` as the entrypoint. Everything else is optional.

```text
my-skill/
├── SKILL.md           # required - main instructions
├── reference.md       # detailed docs, loaded when needed
└── scripts/
    └── validate.sh    # script Claude can execute
```

The directory name becomes the command you type, so `.claude/skills/deploy-staging/SKILL.md` gives you `/deploy-staging`. Keep `SKILL.md` under 500 lines and move detailed material into separate files.

Where you put the directory decides who gets the skill:

| Location   | Path                                     | Applies to                     |
| ---------- | ---------------------------------------- | ------------------------------ |
| Enterprise | See managed settings                     | All users in your organization |
| Personal   | `~/.claude/skills/<skill-name>/SKILL.md` | All your projects              |
| Project    | `.claude/skills/<skill-name>/SKILL.md`   | This project only              |
| Plugin     | `<plugin>/skills/<skill-name>/SKILL.md`  | Where the plugin is enabled    |

## YAML Frontmatter

Every `SKILL.md` opens with a YAML block between `---` delimiters. All fields are optional, and only `description` is recommended, because that is what Claude reads to decide when to load the skill.

```yaml
---
name: your-skill-name
description: What it does. Use when user asks to [specific phrases].
---
```

The `description` field drives discoverability. It must state both what the skill does and when to use it; a description that reads like a dictionary definition is harder to match than one with realistic trigger phrases. Put the key use case first: `description` and `when_to_use` are combined and truncated at 1,536 characters in the skill listing, and the listing itself has a budget of 1% of the model's context window.

### Frontmatter Reference

| Field                      | Required    | Purpose                                                                                                  |
| -------------------------- | ----------- | -------------------------------------------------------------------------------------------------------- |
| `name`                     | No          | Display name in skill listings. Defaults to the directory name, which still supplies the command you type |
| `description`              | Recommended | What the skill does and when to use it. Falls back to the first paragraph of the body                     |
| `when_to_use`              | No          | Extra trigger phrases or example requests, appended to `description` in the listing                       |
| `argument-hint`            | No          | Autocomplete hint for expected arguments, such as `[issue-number]`                                        |
| `arguments`                | No          | Named positional arguments for `$name` substitution; space-separated string or YAML list                  |
| `disable-model-invocation` | No          | `true` stops Claude loading the skill on its own, leaving only `/name`. Default `false`                    |
| `user-invocable`           | No          | `false` hides the skill from the `/` menu, leaving only Claude's automatic use. Default `true`             |
| `allowed-tools`            | No          | Tools that skip the permission prompt for the turn that invokes the skill                                 |
| `disallowed-tools`         | No          | Tools removed from Claude's pool while the skill is active                                                |
| `model`                    | No          | Model for the rest of the current turn; accepts `/model` values or `inherit`                              |
| `effort`                   | No          | Effort level while active: `low`, `medium`, `high`, `xhigh`, `max`                                        |
| `context`                  | No          | `fork` runs the skill in an isolated subagent with the body as its prompt                                 |
| `agent`                    | No          | Subagent type used when `context: fork` is set; defaults to `general-purpose`                             |
| `background`               | No          | With `context: fork`, `false` waits for the result in the invoking turn instead of backgrounding it       |
| `paths`                    | No          | Glob patterns limiting automatic activation to matching files                                             |
| `hooks`                    | No          | Hooks scoped to this skill's lifecycle                                                                    |
| `shell`                    | No          | Shell for inline `` !`command` `` blocks: `bash` (default) or `powershell`                                 |

Boolean fields accept `yes`, `no`, `on`, `off`, `1`, and `0` in any letter case alongside `true` and `false`.

The `allowed-tools` field pre-approves tools rather than restricting them: the listed tools run without a permission prompt for the turn that invokes the skill, the grant clears when you send your next message, and everything else stays callable under your normal permission flow. Use `disallowed-tools` when you actually need a tool taken away while the skill is active. For a project skill, both take effect only after you accept the workspace trust dialog, so review skills before trusting a repository.

## Writing the Instruction Body

After the frontmatter, the body is the instruction set Claude follows when the skill activates. Keep it concise: once a skill loads, its rendered content stays in context for the rest of the session, so every line is a recurring token cost. State what to do rather than narrating how or why.

```markdown
---
name: your-skill
description: [...]
---

# Your Skill Name

## Inputs

What the user must provide before the skill can run.

## Steps

1. Read the configuration file.
2. Resolve the target path.
3. Apply the transformation.
4. Report the result.

## Additional resources

- For complete API details, see [reference.md](reference.md)
- For usage examples, see [examples.md](examples.md)
```

Moving detail into linked files is progressive disclosure: the main file stays fast to load, while the deeper documentation is available when Claude needs it. Large reference docs, API specifications, and example collections do not need to enter context every time the skill runs.

## Arguments and Substitutions

Both you and Claude can pass arguments when invoking a skill. The skill body can reference them and a handful of environment values directly.

| Variable                | Expands to                                                                        |
| ----------------------- | --------------------------------------------------------------------------------- |
| `$ARGUMENTS`            | Everything typed after the skill name                                             |
| `$ARGUMENTS[N]` or `$N` | One argument by 0-based index, so `$0` is the first                               |
| `$name`                 | A named argument declared in the `arguments` frontmatter list                     |
| `${CLAUDE_SKILL_DIR}`   | The directory holding this `SKILL.md`, for referencing bundled scripts            |
| `${CLAUDE_PROJECT_DIR}` | The project root                                                                  |
| `${CLAUDE_SESSION_ID}`  | The current session ID                                                            |
| `${CLAUDE_EFFORT}`      | The active effort level                                                           |

The last four are also substituted inside `allowed-tools`, which is what lets a skill run its own bundled script without a permission prompt. [03 Composite](../03-composite/readme.md#scripts) shows that pairing.

## From a Conversation

The most reliable way to encode a workflow is to prove it works interactively first, then extract it into a skill. Work through a single challenging task in a Claude conversation until Claude completes it correctly. The conversation establishes the right sequence of steps, the necessary context, and the inputs Claude needs to ask for. Once the approach is stable, ask Claude to convert that winning sequence into a `SKILL.md`.

```text
Use the solution from this conversation to write a SKILL.md for [task name].
Include the steps we worked out, the trigger phrases that describe this workflow,
and an example showing the expected inputs and output.
```

## Good vs. Bad Descriptions

The `description` field is the single highest-leverage part of any skill. These examples show the difference between a description that triggers reliably and one that does not.

```yaml
# Good: specific with trigger phrases
description: Manages Linear project workflows including sprint planning,
  task creation, and status tracking. Use when user mentions "sprint",
  "Linear tasks", "project planning", or asks to "create tickets".

# Bad: too vague, no trigger phrases
description: Helps with projects.

# Bad: missing when-to-use context
description: Creates sophisticated multi-page documentation systems.
```

## Hands-On Demo

[Create a Skill from a Proven Claude Code Chat](demo-skill-from-conversation.md): prompt Claude to build a dependency-free JavaScript aggregation module, name the decision sequence that produced it, and encode that sequence as a `SKILL.md`.

## Helpful Claude Slash Commands

| Command           | Usage                                                                          |
| ----------------- | ------------------------------------------------------------------------------ |
| `/skills`         | Check the name a new directory will claim before you write `SKILL.md` into it   |
| `/find-skills`    | Look for an existing skill that already does the job before authoring a new one |
| `/permissions`    | Confirm the tools a draft `allowed-tools` list pre-approves                     |
| `/model`          | Test a `model:` override by switching the session model to the same value       |

## Key Topics Covered in This Module

- [Claude Code Skills documentation](https://code.claude.com/docs/en/skills): official reference for file structure, frontmatter fields, and directory layout
- [Frontmatter reference](https://code.claude.com/docs/en/skills#frontmatter-reference): every field, its default, and the version it arrived in
- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices): writing guidance that applies across Claude products
- [Anthropic Skills GitHub repository](https://github.com/anthropics/skills): production-ready example skills to clone and customize
