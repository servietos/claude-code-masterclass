# code-reviewer skill

The code-reviewer skill gives you a structured review of your local changes (staged or working tree) or of a GitHub pull request, covering correctness, maintainability, readability, efficiency, security, edge cases, testability, and project conventions. You get back a summary, findings sorted into Critical, Improvements, and Nitpicks, and a clear Approved or Request Changes verdict with `file_path:line_number` references.

## Install in Claude Code

Pick one location:

- For every project on your machine, copy the `code-reviewer` folder to `~/.claude/skills/code-reviewer/`.
- For one project, copy the `code-reviewer` folder to `<project>/.claude/skills/code-reviewer/`.

The folder must contain `SKILL.md` at its top level. Start a new Claude Code session, type `/`, and check that `code-reviewer` appears in the list.

## Install in Claude.ai

1. Unzip `code-reviewer.zip`, or keep the archive as it is.
2. Open Customize, then Skills, and add a skill from the zip file.
3. Confirm that `code-reviewer` appears in your skill list.

Custom skills need a plan that supports them and code execution turned on.

## Worked example

Start a session in a repository with uncommitted changes and type:

```text
Review my changes before I push. I want to know if anything could break.
```

When the skill loads, Claude reads `git status`, `git diff`, and `git diff --staged`, and replies with the Summary, Findings, and Conclusion sections.

## Measured figures

The baseline sessions (`claude --disallowedTools Skill` against plain `claude` on the planted fixture) were never captured, so this package quotes no figures.
