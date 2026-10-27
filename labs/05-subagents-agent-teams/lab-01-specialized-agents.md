# Build a specialized documentation subagent with brand-voice enforcement

Build a documentation sub-agent by first reasoning through the design in conversation with Claude, then applying a ready-made recipe or your own findings to implement it.

Each step follows the same pattern:

- **Goal** - what this step achieves
- **Discover** - an open conversation prompt to reason through design decisions
- **What to look for** - what to read and evaluate before moving on
- **Recipe** - a complete implementation prompt you can use as-is or adapt from your own findings

**Where the agent file lands:** every recipe below writes to `.claude/agents/docs-agent.md`, and because you open Claude Code inside the lab project, that path resolves inside the lab project, outside this repository's live agent roster. Your own roster stays untouched and `docs-agent` is registered for the lab session only, which is what lets Step 5 spawn it. A finished, validated reference copy lives at [01-docs-agent/docs-agent-solution/.claude/agents/docs-agent.md](01-docs-agent/docs-agent-solution/.claude/agents/docs-agent.md); write your own in the starter and compare after each step.

**Setup:** there is nothing to install. The starter is already in this repo at [01-docs-agent/docs-agent/](01-docs-agent/docs-agent) and already carries a copy of the repository's `brand-voice-code` skill, so the `skills:` entry you add in Step 1 and the rules file you read in Step 3 resolve against the lab project. Confirm it from the repository root:

```bash
ls labs/05-subagents-agent-teams/01-docs-agent/docs-agent/.claude/skills/brand-voice-code
```

Expected: `SKILL.md` and a `references` folder. The command works unchanged in PowerShell.

Paths that point back at the repository itself (the three command files, `.mcp.json`, and the module readme you audit in Step 5) are written as repo-root paths (`/.mcp.json`, `/.claude/commands/`, `/demos/`) in every prompt below.

## Where to Open Claude Code

This lab builds its own harness, so open Claude Code inside the lab project. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves everything you write here inert, with no error to tell you.

The starter is already in this repo, so there is nothing to scaffold: change into it and start the session there. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/05-subagents-agent-teams/01-docs-agent/docs-agent
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `docs-agent` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the command above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere in the repo:

```text
In labs/05-subagents-agent-teams/01-docs-agent/docs-agent create .claude/agents/docs-agent.md with model sonnet and a skills entry for brand-voice-code ....
```

That works for any step whose result is just files. It does not work for the agent itself: `.claude/agents/` and `.claude/skills/` load from the directory the session was launched in, so a root session writes `docs-agent.md` into the lab folder and then ignores it, along with the `brand-voice-code` skill that ships there, leaving Step 5 with no sub-agent to spawn. Launch inside `docs-agent` from Step 1 onward.

Launching inside the starter makes it the project and the repository a monorepo around it: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session and you read them from the repo root, without ever writing into them, and every path in the prompts below is relative to the lab folder.

---

## Step 1: Design the Agent

**Goal:** Reason through the tools, model, and permission model for a documentation agent before writing any YAML.

**Discover:**

```text
I want to build a documentation sub-agent for this repository. Help me think through the design before I write the agent file:

1. What tools should a docs agent have? Does it need Bash, or is read/write file access enough?
2. Which model makes sense for documentation work? When would you choose a smaller model over the flagship?
3. A sub-agent cannot type a slash command. If this agent needs to reach a skill, which tool or frontmatter field gives it that reach?
4. This agent will enforce brand-voice rules from .claude/skills/brand-voice-code/references/rules.md. Read that file and recommend: should those rules go in the agent body, or is there a better mechanism?

Give me a short recommendation for each with your reasoning.
```

**What to look for:** Claude should argue that docs agents rarely need Bash, discuss cost tradeoffs between haiku and sonnet for writing tasks, and weigh embedding rules in the body against referencing them via a skill. On question 3 the only two correct answers are the `Skill` tool and the `skills:` frontmatter field; if Claude proposes typing `/brand-voice-code`, correct it. If you disagree with any recommendation, push back before moving on.

**Recipe:**

```text
Create a file at .claude/agents/docs-agent.md with the following content:

---
name: docs-agent
description: Writes and improves documentation for this masterclass repository. Enforces brand-voice rules, researches libraries via MCP, and follows the repo's course-authoring command files whenever one covers the task.
model: sonnet
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Skill
skills:
  - brand-voice-code
---

You are a documentation specialist for the Claude Code Masterclass repository.
```

> The recipe above reflects one possible design. If your discovery conversation led to different tool choices or a different model, use those instead. The frontmatter keys are fixed by the [sub-agent frontmatter reference](https://code.claude.com/docs/en/sub-agents); the values inside them are yours to decide.

---

## Step 2: Choose and Configure the Documentation MCPs

**Goal:** Identify which MCPs in this project would help a docs agent, then wire in the ones you choose.

**Discover:**

```text
Read /.mcp.json (the repository's MCP registration) and list every registered MCP server. For each one:
  - Describe what it does in one sentence.
  - Say whether it would be useful to a documentation agent and why.

Then recommend which MCPs a docs agent should have, focusing on writing and improving content that references libraries, frameworks, and Microsoft technologies.
```

**What to look for:** Claude should identify context7 (live library docs) and microsoft-learn (Azure and .NET docs) as strong candidates, and explain why others (playwright, azure-deploy, chrome-devtools) are out of scope for a docs agent. Verify it reads the repository's actual `.mcp.json` file for connection details and guesses no URL.

**Recipe:**

```text
Update .claude/agents/docs-agent.md.

1. Add an mcpServers block to the frontmatter:

mcpServers:
  context7:
    type: http
    url: https://mcp.context7.com/mcp
  microsoft-learn:
    type: http
    url: https://learn.microsoft.com/api/mcp

2. Extend the tools list with these five MCP tools:
  - mcp__context7__resolve-library-id
  - mcp__context7__query-docs
  - mcp__microsoft-learn__microsoft_docs_search
  - mcp__microsoft-learn__microsoft_docs_fetch
  - mcp__microsoft-learn__microsoft_code_sample_search

3. Add a "## Documentation Research" section in the body with this routing rule:
   - Use context7 resolve-library-id then query-docs before writing about any library or framework.
   - Use microsoft-learn microsoft_docs_search when the topic involves .NET, Azure, or any Microsoft technology.
```

Both servers are registered in the repository's `.mcp.json` with exactly these values, so the shorter reference form `mcpServers: [context7, microsoft-learn]` would work in a session launched there. Your session is launched in the lab project, which ships no `.mcp.json`, so the inline definitions above are what actually gives the agent its servers. Inline definitions also earn their keep when you want a server available to this agent only and out of the main conversation's context, which is the real lesson of the field.

> The recipe above adds context7 and microsoft-learn based on a standard recommendation. If your discovery led you to different MCP choices, configure those instead, copying the connection details from the repository's `.mcp.json` exactly.

---

## Step 3: Embed Brand-Voice Rules

**Goal:** Put the brand-voice ruleset in reach of the agent so it enforces the rules on every documentation task.

**Discover:**

```text
Read .claude/skills/brand-voice-code/references/rules.md. Summarize what each rule in that file requires in plain terms, and tell me how many there are. Then tell me: if an agent has these rules in its body, will it apply them automatically, or does it need an explicit instruction to check its output against them before responding?
```

**What to look for:** The file currently defines seven rules. If Claude reports a different number, it summarized from memory and skipped reading the file, so send it back. It should also explain the difference between passive context and active instructions. A rule listed in the body is context; without an explicit "check your output against these rules before responding" instruction, the agent may treat them as background knowledge and never run them as a checklist.

**Recipe:**

```text
Update .claude/agents/docs-agent.md. After the existing body text, add a section titled "## Brand Voice Rules" that names .claude/skills/brand-voice-code/references/rules.md as the single source of truth and summarizes all seven rules as a numbered checklist. Then add one line at the top of the body, before the rules section:

Before finalizing any documentation output, check it against every rule in the Brand Voice Rules section and fix violations before responding. Read the rules file itself before an audit; the checklist below is a summary, and the rules file stays the source of truth.
```

> Because Step 1 added `skills: [brand-voice-code]`, the skill body is preloaded and the agent can also reach the full rules file through the `Skill` tool. Pointing at the file, with no rule count frozen in two places, is what keeps the agent correct when the ruleset grows again. If your discovery conversation surfaced a different enforcement approach, apply that instead.

---

## Step 4: Wire in the Authoring Commands

**Goal:** Teach the agent about the three course-authoring commands so it follows them whenever one covers the task.

Course authoring in this repo lives in three command files under the repository's `/.claude/commands/` at the repo root. A command file is a prompt template: typing `/create-teaching` makes the CLI expand that file into your turn. A sub-agent cannot type a slash command, so it reaches the same behavior by reading the command file and following it. The `brand-voice-code` skill that ships in the lab project is the other half of the surface, and a sub-agent does reach that one through the `Skill` tool.

**Discover:**

```text
Read .claude/skills/brand-voice-code/SKILL.md in this lab project and the repository's three command files: /.claude/commands/create-teaching.md, /.claude/commands/create-lab.md, and /.claude/commands/scaffold-module-folders.md. For each one, tell me:
  - What task it performs
  - The exact trigger situation where a docs agent should follow it and generate nothing of its own

Then suggest how to phrase the instruction in the agent body so the agent reaches for each file as its first move. The agent cannot type a slash command, so phrase it as reading the file.
```

**What to look for:** The trigger descriptions should be specific enough to guide automatic selection. "Use when asked to improve a module" is better than "use for documentation tasks." Watch the mechanism too: a sub-agent has no way to type a slash command, so the instruction must say "read the command file and follow it", never "run /create-teaching". If the suggestions are too vague, ask Claude to sharpen them before moving on.

**Recipe:**

```text
Update .claude/agents/docs-agent.md. Add a section titled "## Available Authoring Commands" with the following content:

Course authoring lives in three command files in the repository above this lab project. Read the file and follow it:

- /.claude/commands/create-teaching.md - enrich a module readme.md with a description, a topic-specific slash-command table, and key documentation links; use when asked to improve, expand, or document an existing module
- /.claude/commands/create-lab.md - scaffold a lab guide at labs/<module>/lab-<nn>-<slug>.md in one of three shapes (guided, prompt-based, discover-recipe); use when asked to add a new lab or exercise
- /.claude/commands/scaffold-module-folders.md - create the numbered topic subfolders for a module, each with a readme.md and a pptx/ subfolder; use when asked to add a new module to the curriculum
- brand-voice-code (skill in this project) - the brand-voice audit; invoke it through the Skill tool after writing or significantly editing any README

Never invoke the three command files by typing a slash command. A sub-agent reads a command file; it reaches a skill through the Skill tool or a preloaded skills: frontmatter entry.
```

> The distinction in the last line is the real lesson of this step. Slash commands are a user-facing surface, so a sub-agent that is told to "run /create-teaching" will either improvise or stall. Pointing it at the file path gives it the same instructions through a mechanism it actually has.

---

## Step 5: Verify the Docs Agent

**Goal:** Confirm the agent is operational and that its brand-voice rules actually work in practice.

**Discover:**

```text
Use the docs-agent sub-agent to audit /demos/05-subagents-agent-teams/01-introduction/readme.md for brand-voice violations. The agent should:
  1. Read the file.
  2. Check it against every rule in its Brand Voice Rules section.
  3. Return a structured report listing each violation with the paragraph or line where it occurs and which rule it breaks.
  4. Do not fix the file.

After the agent returns its report, evaluate it: did it apply the rules correctly, and did it flag anything that is not actually a violation?
```

**What to look for:** This file is close to clean. It contains no em dashes, its Mermaid labels already use quoted `<br/>` syntax, no paragraph runs past four sentences, and all its documentation links point at the current host. The honest report is short or empty. If the agent invents violations to look useful, that is the false-positive failure mode, and it is the one you are here to catch. Weak rule phrasing in the agent body is usually what causes it, so adjust the body and re-run.

> To exercise the miss case as well, copy the file into your lab folder, paste an em dash into one paragraph and change one Mermaid label from `<br/>` to `\n`, then re-run the audit against the copy. An agent that catches both, and only those two, has rules written clearly enough to trust.
