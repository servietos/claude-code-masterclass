# Solution: The Generated Project, Verified

[The topic page](../readme.md) draws the project structure and lists the commands. This folder is the same information taken from a real `specify init` for Claude Code on 2026-10-17, so you can check the tree against a real run.

Environment: Windows 11, `specify` 1.2.1, Claude Code 2.1.302, `uv` 0.9.18, Python 3.12.10.

## Every file init wrote

```bash
specify init meeting-cost --integration claude --script py --non-interactive
cd meeting-cost
find . -type f | sort
```

```text
.claude/skills/speckit-analyze/SKILL.md
.claude/skills/speckit-checklist/SKILL.md
.claude/skills/speckit-clarify/SKILL.md
.claude/skills/speckit-constitution/SKILL.md
.claude/skills/speckit-converge/SKILL.md
.claude/skills/speckit-implement/SKILL.md
.claude/skills/speckit-plan/SKILL.md
.claude/skills/speckit-specify/SKILL.md
.claude/skills/speckit-tasks/SKILL.md
.claude/skills/speckit-taskstoissues/SKILL.md
.specify/.gitignore
.specify/init-options.json
.specify/integration.json
.specify/integrations/claude.manifest.json
.specify/integrations/speckit.manifest.json
.specify/memory/.constitution-template.json
.specify/memory/constitution.md
.specify/scripts/powershell/check-prerequisites.ps1
.specify/scripts/powershell/common.ps1
.specify/scripts/powershell/create-new-feature.ps1
.specify/scripts/powershell/resolve-template.ps1
.specify/scripts/powershell/setup-plan.ps1
.specify/scripts/powershell/setup-tasks.ps1
.specify/scripts/python/check_prerequisites.py
.specify/scripts/python/common.py
.specify/scripts/python/create_new_feature.py
.specify/scripts/python/resolve_template.py
.specify/scripts/python/setup_plan.py
.specify/scripts/python/setup_tasks.py
.specify/templates/checklist-template.md
.specify/templates/constitution-template.md
.specify/templates/plan-template.md
.specify/templates/spec-template.md
.specify/templates/tasks-template.md
.specify/workflows/speckit/workflow.yml
.specify/workflows/workflow-registry.json
```

Four things to read out of that listing:

There is no `specs/` directory and no source folder. The topic page's tree shows both because they appear later, `specs/` on the first `/speckit-specify` run and the package when you implement.

There is no `git init`. The generated folder is not a repository until you make it one, and the Spec Kit scripts run without one.

`.specify/memory/constitution.md` exists already, as a template full of placeholders. `/speckit-constitution` fills it in; it does not create it.

`.claude/` holds skills and nothing else: no `settings.json`, no `CLAUDE.md`, no `commands/` folder. Your own Claude Code configuration for the project stays yours.

## The ten skills

One directory per command under `.claude/skills/`, each holding a `SKILL.md`. The `name` in its front matter is the name you type:

```bash
head -11 .claude/skills/speckit-plan/SKILL.md
```

```text
---
name: "speckit-plan"
description: "Execute the implementation planning workflow using the plan template to generate design artifacts."
argument-hint: "Optional guidance for the planning phase"
compatibility: "Requires spec-kit project structure with .specify/ directory"
metadata:
  author: "github-spec-kit"
  source: "templates/commands/plan.md"
user-invocable: true
disable-model-invocation: false
---
```

`user-invocable: true` puts the skill in the slash menu. `disable-model-invocation: false` also lets Claude load it on its own when a request matches the description.

One of the ten is on its way out. The `speckit-taskstoissues` skill opens with this notice:

```text
> ⚠️ `/speckit-taskstoissues` is deprecated and will be removed in a future minor release. Use the bundled `github` extension instead: run `specify extension add github`, then invoke `/speckit-github-taskstoissues`.
```

## Script flavour

`--script` decides which directory appears under `.specify/scripts/`. Three runs, three outcomes:

| `--script` | Directories written |
| --- | --- |
| `sh` | `.specify/scripts/bash/` |
| `ps` | `.specify/scripts/powershell/` |
| `py` | `.specify/scripts/powershell/` and `.specify/scripts/python/` |

`py` writes two, which is why the topic page's tree annotation names all three outcomes. The demo's setup scripts pass `ps` from PowerShell and `sh` from Bash.

## The feature folder after a full run

This is `specs/001-meeting-cost-calculator/` in the [reference solution](../meeting-cost-solution/readme.md), after specify, plan, tasks, implement and converge:

```text
specs/001-meeting-cost-calculator/
├── checklists/
│   └── requirements.md
├── contracts/
│   ├── calculation.md
│   └── cli.md
├── data-model.md
├── plan.md
├── quickstart.md
├── research.md
├── spec.md
└── tasks.md
```

## If the version has moved on

Re-run the commands at the top. A changed listing means the topic page needs correcting; the listing here is what 1.2.1 produced.

[← Back to The Spec-Driven Workflow](../readme.md)
