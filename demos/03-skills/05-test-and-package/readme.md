# Test and Package Skills

A skill that works on your machine is not yet a product. Publishing turns a local folder into an artifact someone who has never seen your repository can install, run, and judge. Everything on this page is about the two questions that decide whether that handover survives: does the skill load when a stranger phrases the request their own way, and once loaded does it produce what it promised.

## What Decides Whether a Skill Loads

Only the `description` frontmatter field is in context before a skill loads. The body, the references, and the scripts cost nothing and influence nothing until the decision has already been made, which is why adding trigger keywords to the body changes exactly nothing.

The decision is observable. When a skill loads, the transcript contains a tool call named `Skill`, so a headless run plus a search for that name is a yes-or-no answer rather than an impression. Both directions matter: a skill that fires on unrelated work gets switched off as fast as one that never fires at all.

## Measuring It Instead of Predicting

Reading a description and predicting which prompts will match it is a reasonable first pass and a poor test. Run the prompt instead:

```bash
claude -p "Review my changes." --output-format stream-json --verbose \
  --strict-mcp-config --disallowedTools Edit Write NotebookEdit Bash PowerShell
```

| Flag | Why it is there |
|---|---|
| `--output-format stream-json --verbose` | Emits one JSON object per line so tool calls are visible; `stream-json` requires `--verbose` |
| `--strict-mcp-config` | Starts no MCP servers, which otherwise dominate the wall time of every run |
| `--disallowedTools Edit Write NotebookEdit Bash PowerShell` | A measurement must not modify the project it is measuring |

Two traps live in that command. `--allowedTools` is an auto-approve list and not a restriction, so a sweep that names it still edits files; only `--disallowedTools` removes a tool. And denying *every* tool biases the answer upward, because it leaves loading the skill as the only move the session has left.

Loading is a model decision, not a lookup, so the same prompt can load on one run and not the next. A trigger row is therefore a count over several runs, and a row that comes back 2 of 3 is a finding in its own right rather than a pass.

## The Four Layers of a SKILL.md

Every failure a test exposes belongs to exactly one layer, and editing the wrong one produces a change that feels productive and fixes nothing.

| Layer | Controls | The failure it owns |
|---|---|---|
| `description` frontmatter | Whether the skill loads at all | Never fires, or fires on unrelated work |
| Workflow steps | What gets gathered | The change the review never saw |
| Analysis pillars | What gets noticed | A whole defect class the review skipped |
| Feedback structure | How findings are reported | No line numbers, no verdict, no coverage statement |

## What a Local-Changes Workflow Can Actually See

A workflow step that names specific commands inherits everything those commands cannot see. `git diff` and `git diff --staged` never show an untracked file: a file created five minutes ago appears only as `??` in `git status`, so a gather step built on the two diffs is blind to it. The same gap arrives from the other direction once work is committed on a branch, where both diffs are empty and only `git diff <base>...HEAD` surfaces anything.

## Proving It Is Worth Adopting

Adoption arguments are won with numbers, and the control run has to be honest. Asking a model to ignore a skill it has already loaded is not a control; starting the session with `claude --disallowedTools Skill` removes the tool so nothing on disk has to move. `/cost` prints to the terminal and writes nothing to disk, so its totals are copied across by hand, and a figure nobody captured is written as "not measured" rather than estimated.

## Distribution Model

Skills are distributed as folders containing `SKILL.md` and any companion files. Individual users download the folder, zip it if needed, and upload it via Settings > Capabilities > Skills in Claude.ai, or place it in the Claude Code skills directory. Organization admins can deploy skills workspace-wide for automatic rollout and centralized management.

Skills have been published as an open standard, portable across tools and platforms. The `compatibility` field in frontmatter lets authors note when a skill is designed to take full advantage of a specific platform's capabilities.

## What Ships and What Stays Behind

The package is the skill folder and nothing else. Test matrices, fixtures, run records and comparison tables are how you built confidence in it, and none of them belong in the archive a stranger installs.

The install README stays outside the folder too. A `README.md` inside a skill folder is not part of the skill contract and only adds tokens to what Claude loads, so host it one level up, next to the folder you ship.

## Using Skills via the API

For programmatic use such as applications, agents, or automated pipelines, the skills API gives direct control over skill management and execution. Add skills to Messages API requests via the `container.skills` parameter and manage versions through the Claude Console. Skills in the API require the Code Execution Tool beta, which provides the sandbox they run in, so a skill that shells out to `git` or `gh` is the common surprise on this route: check what it actually invokes before promising it.

## Positioning Your Skill

How you describe the skill decides whether anyone tries it. Focus on the outcome the user gets, not the mechanism.

Good:
> "The ProjectHub skill enables teams to set up complete project workspaces in seconds, including pages, databases, and templates, instead of spending 30 minutes on manual setup."

Bad:
> "The ProjectHub skill is a folder containing YAML frontmatter and Markdown instructions that calls our MCP server tools."

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/cost` | Read the token total for a with-skill and a without-skill run before claiming a delta |
| `/review` | Review the pull request that ships the skill before it is published |
| `/security-review` | Check `scripts/` for injection risks before public distribution |

## Hands-On Demo

[Test and Package a Skill for Distribution](demo-test-and-package-a-skill.md): measures the `code-reviewer` skill's trigger surface with a headless sweep over a small pricing project, grades what the loaded skill actually reports against a planted defect, patches the layer that owns each failure, and packages the result for another team.

## Key Topics Covered in This Module

- [The Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf): Anthropic's official guide covering testing strategies, distribution model, and API integration (Chapters 3 and 4)
- [Claude Code Skills documentation](https://code.claude.com/docs/en/skills): official reference for skill frontmatter, directory layout, and the `allowed-tools` allowlist
- [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference): the `-p`, `--output-format`, `--strict-mcp-config`, and `--disallowedTools` flags the trigger sweep is built on
- [Anthropic Skills GitHub repository](https://github.com/anthropics/skills): published skills to examine for structure, testing patterns, and distribution conventions
- [Claude Messages API](https://platform.claude.com/docs/en/api/messages): API reference for using skills programmatically via the `container.skills` parameter
