# Create Reusable Skills

A skill is how a procedure you would otherwise re-paste every time becomes something Claude already knows. Once the DOCX skill from the demo below is installed, the library choice, the layout rules, and the generation steps arrive with it, so the request is the entire prompt:

```text
Generate an invoice for the three line items in order.json as a .docx file.
```

Nothing in that prompt names the skill. The same holds for the skills already installed in this repo: asking about module status loads `class-dashboard` on its own.

```text
Which modules are still missing a demo?
```

## What Are Skills?

Skills are installable extensions that give Claude Code domain-specific knowledge and capabilities. Each skill is a folder under `.claude/skills/` holding a `SKILL.md` and whatever supporting files its instructions refer to, and Claude loads that content into the session when the work at hand matches what the skill describes itself as doing. The name is case-sensitive: a lowercase `skill.md` is not discovered on Linux or in CI, so it fails in exactly the place you cannot see it. Compared with a slash command, which is one Markdown file for one repeatable task, a skill is a folder that can carry references, scripts, and multi-step logic, and it is installed rather than committed with the project.

This topic covers what the docx demo below needs: what a skill is, and where skills come from.

## Popular Skill Repositories

Skills are shared as Git repositories or zip archives and installed via Claude Code's `/find-skills` command or by cloning directly into `.claude/skills/`. The table below lists the most widely used sources.

| Repository / Source | Distribution Point | Install Method |
|---------------------|--------------------|----------------|
| [anthropics/skills](https://github.com/anthropics/skills) | GitHub | `claude skills install github:anthropics/skills/<skill-name>` |
| Anthropic Skills Catalog (claude.ai) | Claude.ai web UI → Skills tab | One-click install from the catalog |
| [skills.sh](https://skills.sh) | Open agent skills directory (Vercel, open source) | `npx skills add <owner>/<repo>@<skill-name>` |
| [obra/superpowers](https://github.com/obra/superpowers) | Claude Code plugin marketplace | `/plugin install superpowers@claude-plugins-official` |
| [azure-samples/claude-skills-azure](https://github.com/Azure-Samples) | GitHub | `claude skills install github:Azure-Samples/<repo>/<skill-name>` |
| Team / private repo | Self-hosted Git (HTTPS or SSH) | `claude skills install git+https://your-repo.git` |
| Local folder | Filesystem | `claude skills install ./path/to/skill-folder` |

To discover available skills from within a session, use the `/find-skills` command, which queries the catalog and presents matching results with install instructions.

```text
/find-skills Azure deployment
```

```text
/find-skills security review
```

Installing a skill drops a folder and changes nothing else: no `settings.json` entry, no `CLAUDE.md` edit, and deleting the directory is the entire uninstall.

## Hands-On Demo

[Use a DOCX Skill to create an Invoice Generator](demo-docx-invoice.md) searches the catalog for a DOCX skill, installs it, reads back the `SKILL.md` that landed on disk, and then lets the skill drive a TypeScript program that renders a sample invoice as a `.docx` file.

## Helpful Claude Slash Commands

| Command | Usage |
|---------|-------|
| `/find-skills` | Search the catalog and install skills with domain-specific instructions. |
| `/context` | Confirm what an installed skill actually costs the session before adding more. |
| `/doctor` | Health check the installation and verify a freshly installed skill folder was picked up. |

## Key Topics Covered in This Module

- [Agent Skills](https://code.claude.com/docs/en/skills): authoring, installing, and triggering skills
- [Slash Commands](https://code.claude.com/docs/en/slash-commands): lightweight complement to skills for single-task automation
- [Claude Code Settings](https://code.claude.com/docs/en/settings): the permission model a skill runs under
