# Compose Skills into Workflows

A composite skill is a single skill folder that bundles its main instruction file with companion directories for scripts, reference documentation, and static assets. This layout keeps everything a skill needs self-contained and makes the folder portable across projects and teams. Composition also happens between skills, through stacking, forking into a subagent, and directory-qualified variants.

## Folder Structure

The full layout for a composite skill looks like this:

```text
your-skill-name/
├── SKILL.md           # required - main skill file
├── scripts/           # optional - Python, Bash, or other executables
│   ├── process_data.py
│   └── validate.sh
├── references/        # optional - documentation loaded on demand
│   ├── api-guide.md
│   └── examples/
└── assets/            # optional - templates, fonts, icons
    └── report-template.md
```

`SKILL.md` is always loaded when the skill activates. Files in `scripts/`, `references/`, and `assets/` are loaded only when `SKILL.md` explicitly instructs Claude to read them. This separation keeps the activation path lean while still allowing arbitrarily deep supporting material.

Once loaded, the rendered `SKILL.md` stays in context for the rest of the session, while the branch files enter context only on the turn Claude reads them. That asymmetry is the whole reason to split a large skill.

## Scripts

The `scripts/` directory holds executable files Claude can run as part of a skill workflow. A data-processing skill might call `process_data.py` to transform a CSV before summarizing it; a validation skill might invoke `validate.sh` to lint output before returning results.

Address those scripts through `${CLAUDE_SKILL_DIR}`, which expands to the directory holding `SKILL.md`. Claude runs commands from the project root, not from the skill folder, so a bare relative path misses. The same variable is substituted inside `allowed-tools`, so pairing the two lets the script run without a permission prompt:

```yaml
---
name: report-builder
description: Build a validated report from a CSV file
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/validate.sh *)
---

## Steps

1. Run `${CLAUDE_SKILL_DIR}/scripts/validate.sh` on the target file and capture its output.
2. If validation fails, report the errors and stop.
3. Otherwise, continue with the transformation.
```

Use `${CLAUDE_PROJECT_DIR}` when the skill needs a project-local file instead. Both resolve identically whether the skill is installed at the personal, project, or plugin level.

## References

The `references/` directory holds Markdown documentation that `SKILL.md` loads on demand. The pattern is called progressive disclosure: `SKILL.md` stays small and fast to load, while deep reference material sits in branch files that Claude reads only when the task requires it.

```markdown
## Steps

1. Check which cloud provider the user specified.
2. If Azure, read `references/azure.md` and follow those steps.
3. If AWS, read `references/aws.md` and follow those steps.
```

This conditional loading is the idiomatic pattern for skills that handle multiple domain variants. Each reference file can be as long as needed without bloating the main activation file, which should stay under 500 lines.

### Reference Files vs Playbooks

A branch file can carry either of the two kinds of skill content, and the difference changes how you write it. Reference content is knowledge Claude applies to work already in progress: conventions, patterns, style guides, domain facts. Playbook content is an ordered procedure Claude executes: the steps, their sequence, and what each one produces.

There is no `playbook` frontmatter field and no special file type, so a playbook is simply a reference file written in the imperative. The distinction is a naming convention that pays off in how the router delegates to it:

```markdown
## Delegation Map

| Request | Read |
|---|---|
| Naming, layout, style questions | `references/conventions.md` |
| Provisioning a new environment | `references/provision-playbook.md` |
```

```text
your-skill/
├── SKILL.md                            # router: the map above, plus rules that apply to every branch
└── references/
    ├── conventions.md                  # reference: what good looks like
    └── provision-playbook.md           # playbook: numbered steps, in order, with checkpoints
```

Two rules keep a playbook working. Give a branch file **no YAML frontmatter**, because frontmatter is what makes a stray Markdown file get discovered as a skill in its own right, and never nest a `SKILL.md` inside another skill's folder. The router delegates by telling Claude to read the file, never by calling it as a skill.

Keep in `SKILL.md` anything that must hold regardless of which branch runs, such as a validation gate or a hard constraint. Everything a single procedure needs belongs in that procedure's playbook, where it costs nothing until the procedure is actually chosen.

## Hierarchical Relations Between Skills

The skill system has no formal dependency mechanism: there is no `dependencies:` frontmatter field, no automatic sub-skill triggering, and no shared state between skill executions. Composition instead comes from five documented mechanisms.

**Reference files within one skill.** The `SKILL.md` body instructs Claude to read a specific file in `references/` when a condition is met. This creates a depth hierarchy inside a single folder and is the recommended approach for skills that decompose into multiple sub-concerns.

**Explicit cross-skill references.** A `SKILL.md` can instruct Claude to read any path, including another skill's `SKILL.md`. This works as a manual cross-reference with no formal declaration and no auto-loading. Use it sparingly, because it creates implicit coupling: if the referenced skill is renamed, moved, or uninstalled, the referencing skill silently breaks with no error at load time.

```markdown
## Step 1

If the output format is a Word document, read and follow
`.claude/skills/docx-writer/SKILL.md` before proceeding.
```

**Stacking at invocation.** Several skills can be typed at the start of one message. `/write-tests /fix-issue 123` loads both and passes the trailing `123` as `$ARGUMENTS` to each. Claude Code expands the first skill plus up to five more, stopping at the first token that is not an inline user-invocable skill; that token and everything after it become the argument text.

A skill that runs as a forked subagent, such as `/code-review`, or one whose arguments may themselves begin with a slash command, such as `/loop`, therefore ends the stack at that point.

**Forking into a subagent.** Setting `context: fork` runs a skill in an isolated context with the `SKILL.md` body as the subagent's prompt, and `agent:` selects which subagent type executes it. The fork runs in the background by default, so set `background: false` to wait for the result in the invoking turn. This is composition between a skill and an agent rather than between two skills:

| Approach                     | System prompt            | Task                        | Also loads                                          |
| ---------------------------- | ------------------------ | --------------------------- | --------------------------------------------------- |
| Skill with `context: fork`   | From the agent type      | `SKILL.md` content          | CLAUDE.md, except when the agent is Explore or Plan |
| Subagent with `skills` field | Subagent's markdown body | Claude's delegation message | Preloaded skills plus CLAUDE.md                     |

**Directory-qualified variants.** Skills also load from nested `.claude/skills/` directories below the working directory, which lets a monorepo package ship skills that apply only to that package. When a nested skill shares a name with another skill, both stay available and the nested one appears as `apps/web:deploy`.

Typing `/deploy` runs the project-root skill and appends the list of qualified variants with an instruction to also invoke any whose directory holds the files being worked on. Typing `/apps/web:deploy` runs the nested one explicitly.

## Precedence

When skills share a name across levels, enterprise overrides personal and personal overrides project. A skill at any of those levels overrides a bundled skill of the same name, so a `code-review` skill in your project replaces the bundled `/code-review`. Plugin skills carry a `plugin-name:skill-name` namespace and cannot collide. A skill and a `.claude/commands/` file with the same name resolve in the skill's favor.

## When a Composite Skill Becomes a Plugin

A skill folder that needs to ship more than instructions and assets can carry a `.claude-plugin/plugin.json`. It then loads as a plugin named `<name>@skills-dir` and can bundle agents, hooks, and MCP servers alongside the skill. Inside a project's `.claude/skills/`, this takes effect only after the workspace trust dialog is accepted.

Live change detection covers `SKILL.md` text only. For a skill folder that is also a plugin, edits to `hooks/`, `.mcp.json`, `agents/`, and `output-styles/` need `/reload-plugins` before they apply.

## Practical Example: Invoice Skill

An invoice skill that handles both PDF and DOCX output is a natural fit for the composite pattern. The main `SKILL.md` handles the shared extraction logic, then branches to format-specific reference files:

```text
invoice/
├── SKILL.md
├── scripts/
│   └── extract_line_items.py
└── references/
    ├── pdf-output.md
    └── docx-output.md
```

`SKILL.md` instructs Claude to run `${CLAUDE_SKILL_DIR}/scripts/extract_line_items.py` first, then read `references/pdf-output.md` or `references/docx-output.md` depending on the requested format. Neither reference file needs to know about the other, and the main file stays within the 500-line body budget.

## Real-World Example: dotnet-conventions

The `.claude/skills/dotnet-conventions` skill in this repo demonstrates the composite and delegation patterns at production scale. Its layout is minimal but covers two distinct concern areas through reference files:

```text
dotnet-conventions/
├── SKILL.md
└── references/
    ├── conventions.md    # naming, architecture, DI, testing, logging, code style
    └── dotnet-cli.md     # build, test, run, publish, format, NuGet
```

### Delegation Map

`SKILL.md` never handles build tooling and code conventions in the same place. Instead it declares an explicit delegation map at the top of its body:

| Request type | Reference file to read |
|---|---|
| Build, test, run, publish, format, or manage NuGet packages | `references/dotnet-cli.md` |
| Naming, architecture, DI, testing, logging, and code style | `references/conventions.md` |

When Claude activates the skill it reads the map first, determines which reference file the current request falls under, then loads only that file. A build request never pulls in the conventions document; a naming question never pulls in CLI procedures. This keeps each activation lean and avoids context bloat from irrelevant material.

The `SKILL.md` also declares a hard rule at the top: always validate against Microsoft Learn via the `microsoft-learn` MCP before applying any SDK pattern. This is a single-line constraint in `SKILL.md` that applies regardless of which reference file is delegated to, making it an ideal candidate for the main activation file rather than either branch.

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/update-config` | Grant `Bash` permissions when `scripts/` executables are blocked |
| `/fewer-permission-prompts` | Discover which tool calls the skill's scripts make repeatedly across sessions |
| `/permissions` | Verify all tools the composite skill needs are permitted before running |
| `/reload-plugins` | Apply changes to `hooks/`, `agents/`, or `.mcp.json` in a skill folder that is also a plugin |

## Key Topics Covered in This Module

- [Claude Code Skills documentation](https://code.claude.com/docs/en/skills): official reference for skill folder layout, frontmatter fields, and the reference-file loading pattern
- [Subagents documentation](https://code.claude.com/docs/en/sub-agents): the `context: fork` counterpart, including preloading skills into a subagent
- [Anthropic Skills GitHub repository](https://github.com/anthropics/skills): production composite skills to examine for structure and progressive disclosure patterns
- [Plugins reference](https://code.claude.com/docs/en/plugins-reference): turning a skill folder into a plugin that also ships agents, hooks, and MCP servers
