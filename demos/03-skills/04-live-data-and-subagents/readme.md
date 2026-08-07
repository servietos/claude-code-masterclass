# Inject Live Data and Fork Skills into Subagents

Two advanced patterns change what a skill is: dynamic context injection puts real data into the prompt before Claude reads it, and `context: fork` runs the skill as an isolated subagent instead of inline. The first removes a round trip, since Claude never has to ask for the data it needs. The second removes the skill's output from your main context, since only the subagent's summary comes back.

## Dynamic Context Injection

The `` !`<command>` `` syntax runs a shell command before the skill content is sent to Claude and replaces the placeholder with the command's output. Claude receives a fully rendered prompt with the data already in it.

```markdown
## Current changes

!`git diff HEAD`

## Instructions

Summarize the changes above in two or three bullet points, then list any risks.
```

The order of operations matters for understanding what this is:

1. Each `` !`<command>` `` executes immediately, before Claude sees anything.
2. The output replaces the placeholder in the skill content.
3. Claude receives the finished prompt with actual data.

This is preprocessing, not tool use. Claude never decides to run these commands, never sees them as commands, and cannot be talked out of running them. The distinction shows up in the transcript: no `Bash` tool call appears, because none happened.

### Syntax Rules

Substitution runs once over the original file. Command output is inserted as plain text and is not re-scanned, so a command cannot emit a placeholder for a later pass to expand.

The inline form is recognized only when `!` sits at the start of a line or immediately after whitespace. In `` KEY=!`cmd` `` the placeholder stays literal text and nothing runs.

For multi-line commands, use a fenced block opened with ` ```! ` instead:

````markdown
## Environment

```!
node --version
npm --version
git status --short
```
````

### Shell Selection and Policy

Commands run through Bash by default. Set `shell: powershell` in the frontmatter to run them through PowerShell instead, which requires the PowerShell tool: on by default on Windows without Git Bash, and enabled elsewhere with `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`.

Administrators can switch the whole mechanism off with `"disableSkillShellExecution": true` in settings. Each command is then replaced with `[shell command execution disabled by policy]` rather than being run. The setting covers user, project, plugin, and additional-directory skills, but not bundled or managed ones, and it is most useful in managed settings where users cannot override it.

## Running a Skill in a Subagent

Adding `context: fork` runs the skill in an isolated context. The rendered `SKILL.md` becomes the subagent's prompt, and the subagent has no access to your conversation history. Whatever it reads stays in that context and is discarded; only its final answer comes back to you.

```yaml
---
name: pr-summary
description: Summarize changes in a pull request
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Pull request context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`

## Your task
Summarize this pull request...
```

The `agent` field picks the execution environment: model, tools, and permissions. Three agents are built in:

- `Explore`: read-only, finds and reads code, returns what it found
- `Plan`: read-only, returns a step-by-step implementation plan
- `general-purpose`: full toolset, can write and edit

Any custom subagent in `.claude/agents/` can be named here too. Omitting the field gives you `general-purpose`. Explore and Plan skip CLAUDE.md and git status to stay small, so a forked skill on those agents sees only the `SKILL.md` content and the agent's own system prompt.

### Background by Default

A forked skill runs in the background: you keep working, and the result arrives in the conversation when it finishes. Set `background: false` to wait for the result inside the turn that invoked the skill.

Claude Code waits for the result regardless of that setting in four cases:

- Non-interactive mode, with the `-p` flag or the Agent SDK
- `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` set to `1`
- Invoking a forked skill while an earlier run of the same skill is still going
- A scheduled task firing with the skill as its prompt

A backgrounded fork also runs with the narrower tool set that applies to background subagents. If the skill's steps need a tool outside that set, set `background: false` to keep the full one. Edits made by a backgrounded fork land outside your session's checkpoints, so `/rewind` does not undo them and you need git to revert.

### Fork Only Actionable Skills

`context: fork` makes sense only for skills that contain a task. A skill holding guidelines such as "use these API conventions" gives the subagent material but nothing to do, and it returns without meaningful output.

## Combining Both

The two patterns are strongest together: injection gathers the evidence, the fork spends the tokens analyzing it somewhere else. A review skill can inline the diff, the test output, and the changed-file list, then hand all of it to an Explore agent whose findings return as a short summary. Your main context receives the summary, not the raw diff.

To request deeper reasoning during either pattern, include `ultrathink` anywhere in the skill content.

## Hands-On Demo

[Inject Live Project Data and Fork the Audit](demo-live-context-and-fork.md): build a skill that inlines a project's file listing and open TODOs with `` !`command` ``, then fork the same evidence into an Explore subagent and compare what each one costs your main context.

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/context` | Compare what an inline skill and a forked skill leave behind in the main context |
| `/agents` | Print the location of the subagent definitions the `agent:` field can name |
| `/rewind` | Confirm the checkpoint gap: edits from a backgrounded fork are not restored here |
| `/permissions` | Check the `allowed-tools` grants a forked skill needs before it runs unattended |

## Key Topics Covered in This Module

- [Advanced patterns in the Skills documentation](https://code.claude.com/docs/en/skills#advanced-patterns): official reference for dynamic context injection and forked execution
- [Subagents documentation](https://code.claude.com/docs/en/sub-agents): agent types, foreground and background execution, and preloading skills
- [Settings reference](https://code.claude.com/docs/en/settings): `disableSkillShellExecution` and the environment variables that change fork behavior
