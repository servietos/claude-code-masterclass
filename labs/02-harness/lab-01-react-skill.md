# Install a React Agent Skill

Install a ready-made React skill from [skills.sh](https://www.skills.sh/) and confirm it is active before the harness lab uses it.

Each step follows the same pattern:

- **Overview**: what this step achieves
- **Research / Planning / Discussion**: an open prompt to reason through the problem before acting
- **Finding**: what to read and evaluate before moving on
- **Recipe**: a complete implementation prompt you can use as-is or adapt from your own findings
- **Expected Outcome**: observable artefacts that confirm success

---

## Where to Open Claude Code

This lab builds its own harness, so open Claude Code inside the lab project rather than at the repo root. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves everything you write here inert, with no error to tell you.

The starter is already in this repo, so there is nothing to scaffold: change into it and start the session there. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/02-harness/lab-01-react-skill
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `lab-01-react-skill` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the command above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere in the repo:

```text
In labs/02-harness/lab-01-react-skill install the vercel-labs react-best-practices skill ....
```

That works for any step whose result is just files. It does not work for the skill itself: `.claude/skills/` loads from the directory the session was launched in, so a root session writes the skill into the lab folder and then ignores it. Launch inside the starter from Step 1 onward.

Restart the session with `/exit` then `claude` after any edit to `.claude/settings.json`, because hook configuration is read at startup.

Launching inside the starter is what makes the repository a monorepo to this lab rather than the project: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session. Nothing in this lab writes into them, and every path in the prompts below is relative to the lab folder.

The lab project is a copy of the React app, the same app Lab 02 works on, so the skill you install here is one folder copy away from the harness Lab 02 builds.

The finished reference lives beside the starter at `labs/02-harness/lab-01-react-skill-solution/`; open it only if you get stuck.

---

## Step 1: Understand Agent Skills

**Overview:** Before installing anything, build a clear mental model of what a skill is and where it lives. Claude Code loads skills automatically from a known directory; knowing the structure means you can evaluate any ready-made skill before trusting it.

**Research / Planning / Discussion:**

```text
Read the skills Anthropic publishes in its official repository, github.com/anthropics/skills,
which skills.sh lists at https://www.skills.sh/anthropics/skills. Compare frontend-design, pdf
and skill-creator under skills/.

Answer these questions:
1. What directory path do skills live in once they are installed in a project?
2. What frontmatter fields appear at the top of a skill file, and what does each one do?
3. How does Claude know when to use a skill versus ignoring it?
4. What is the difference between a skill that is a single SKILL.md and one that ships extra files?
```

**Finding:** Claude should fetch the actual `SKILL.md` files before answering rather than stating generic facts. The answer to question 1 must be `.claude/skills/<skill-name>/SKILL.md` inside the project root, and the project root is whichever directory the session was launched in: here that is the React app, not the repository. Question 2 should name `name`, `description`, and the optional `license`, `allowed-tools` and `disallowed-tools`; there is no `tools` field. None of the three skills restricts its tools: `frontend-design` and `pdf` carry `name`, `description` and `license`, while `skill-creator` carries only `name` and `description`.

Question 3 should explain that the `description` field drives automatic selection and that explicit invocation ("use the vercel-react-best-practices skill") always works. Question 4 should note that `frontend-design` ships only `SKILL.md` and `LICENSE.txt`, `pdf` adds `forms.md`, `reference.md` and a `scripts/` folder, and `skill-creator` adds `references/`, `scripts/`, `agents/`, `assets/` and `eval-viewer/`; Claude reads those files only when `SKILL.md` points it at them. Push back if Claude describes skills as a general AI concept rather than reading the actual files.

**Recipe:**

```text
Fetch the SKILL.md of frontend-design, pdf and skill-creator from github.com/anthropics/skills.
For each skill, summarize: the name, the description field, whether it declares allowed-tools,
and which supporting files it ships beside SKILL.md. Then explain the general structure: what
files are required, what fields are required in the frontmatter, and how Claude decides to load
a skill during a session.
```

**Expected Outcome:** Claude produces a structured comparison of the three Anthropic skills and explains the skill contract clearly: a `SKILL.md` file with `name` and `description` frontmatter, optional `license` and `allowed-tools` fields, and optional supporting files the skill delegates to. Claude also reports that none of the three declares `allowed-tools`.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 2: Find a Ready-Made React Skill on skills.sh

**Overview:** skills.sh is the directory of ready-made agent skills. Rather than writing a React skill from scratch, find one there and judge honestly what it does and does not cover.

**Research / Planning / Discussion:**

```text
I want a ready-made React skill for Claude Code instead of writing one from scratch.

Search skills.sh (https://www.skills.sh/) for React skills. Which repository publishes each one,
what does the React skill cover, and how would I install it?
```

**Finding:** Claude should land on `vercel-react-best-practices`, published by `vercel-labs/agent-skills` at `https://www.skills.sh/vercel-labs/agent-skills/vercel-react-best-practices`, whose page shows the install command `npx skills add https://github.com/vercel-labs/agent-skills --skill vercel-react-best-practices`. The source repository ships `composition-patterns`, `deploy-to-vercel`, `react-best-practices`, `react-native-skills`, `react-view-transitions`, `vercel-cli-with-tokens`, `vercel-optimize`, `web-design-guidelines` and `writing-guidelines` under `skills/`. There is no directory called `skills/react`, so a claim that one exists is a hallucination.

The skill's source folder is `skills/react-best-practices`, and its frontmatter name is `vercel-react-best-practices`. Its scope is React and Next.js performance optimization: 70 rules across eliminating waterfalls (`async-`), bundle size (`bundle-`), server-side performance (`server-`), client-side data fetching (`client-`), re-render optimization (`rerender-`), rendering performance (`rendering-`), JavaScript performance (`js-`) and advanced patterns (`advanced-`). It carries no rule about controlled form inputs, so do not expect it to design the Lab 02 checkout form for you. Push back if Claude invents a skill that has no skills.sh page, or if it proposes writing a custom skill when a ready-made one already exists.

**Recipe:**

```text
Open https://www.skills.sh/vercel-labs/agent-skills/vercel-react-best-practices and report the
install command it shows. Then open its source repository, vercel-labs/agent-skills on GitHub,
list the directories under skills/, open skills/react-best-practices and describe: the name and
description in its frontmatter, the files it ships, and the rule categories under rules/.

Then tell me which folder under .claude/skills/ the install will create in this project, given
the frontmatter name.
```

**Expected Outcome:** Claude reports the skills.sh page and its install command, identifies `skills/react-best-practices` inside `vercel-labs/agent-skills`, reports the frontmatter name `vercel-react-best-practices`, lists the shipped files (`SKILL.md`, `AGENTS.md`, `README.md`, `metadata.json`, `rules/`), and names the eight rule-category prefixes. The target folder is `.claude/skills/vercel-react-best-practices/`.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 3: Install and Verify

**Overview:** Install the skill into the React app and confirm Claude can invoke it. It lands in the app's own `.claude/skills/`, the same project-relative path Lab 02 launches from, so copying that one folder across makes the skill discoverable for Tasks 5 and 6 of Lab 02 where it drives the review of the Checkout button fix. Nothing goes into the repository's `.claude/`.

**Research / Planning / Discussion:**

```text
I want to install vercel-react-best-practices from skills.sh into this project at
.claude/skills/, meaning the React app I launched this session in, not the repository root.
Walk me through the installation options:

1. Can I use the npx skills add command from its skills.sh page as it is, or does Claude Code
   need extra flags when you run it for me?
2. What is the exact target path inside this project, given that the skill's frontmatter name is
   vercel-react-best-practices?
3. After copying, how do I confirm Claude has picked up the skill without restarting the session?
4. Is there anything in the skill files I should review before trusting them?
```

**Finding:** Claude should add three flags to the skills.sh command, because it runs the command non-interactively: `-a claude-code` targets Claude Code's `.claude/skills/`, `--copy` writes a real folder instead of a symlink (Lab 02 copies that folder across), and `-y` skips the confirmation prompts. The target path must be `.claude/skills/vercel-react-best-practices/` inside the React app, which is `labs/02-harness/lab-01-react-skill/.claude/skills/vercel-react-best-practices/` seen from the repo root. The folder name matches the frontmatter `name`; a hand copy to `.claude/skills/react/` would create folder-versus-frontmatter drift.

The CLI installs the whole skill folder, including the `rules/` subdirectory the skill delegates to. For confirmation, Claude should suggest explicitly invoking the skill by name ("use the vercel-react-best-practices skill") on a small test task. Reviewing the skill files before use is good practice; Claude should name the frontmatter `description`, any `allowed-tools`, and the security assessment the CLI prints before it installs as the first things to check.

**Recipe:**

```text
Install the vercel-react-best-practices skill from skills.sh into this project, the React app I
launched the session in, with this command:

npx -y skills add https://github.com/vercel-labs/agent-skills --skill vercel-react-best-practices -a claude-code --copy -y

Do not write into the repository's /.claude/ at the repo root. After installing, confirm that
.claude/skills/vercel-react-best-practices/ holds SKILL.md and the rules/ subdirectory, then read
the skill's SKILL.md and summarize what it covers. Then invoke the skill on this app: read
src/components/ShopItem.tsx and tell me which of the skill's rules apply to that component
and which do not.
```

**Expected Outcome:** The CLI prints a security assessment table for `vercel-react-best-practices`, then `Installed 1 skill` with the skill marked `(copied)`. The directory `.claude/skills/vercel-react-best-practices/` exists inside the React app with `SKILL.md`, `AGENTS.md`, `README.md` and a `rules/` subdirectory, and `skills-lock.json` at the app root records `vercel-labs/agent-skills` as the source. Claude reads the manifest and summarizes the skill as a React and Next.js performance rule pack. The test invocation on `ShopItem.tsx` produces a short assessment that cites named rules, including the honest observation that most of the bundle and server-side rules do not apply to a small Create React App component. The skill is now ready for Lab 02.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.
