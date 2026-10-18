---
presents: demo-docx-invoice.md
budget: 4 min
beats: 3
---

# Present: Use a DOCX Skill to create an Invoice Generator

A skill searched for, installed, and then left to drive a TypeScript invoice generator. A room walks away knowing that installing a skill only drops a folder, and that its value is the domain contract handed over before any code exists.

------

This topic ships no `-solution` folder: the run leaves an installed skill folder under [`.claude/skills/`](../../../.claude/skills) at the repo root and a generated `invoice/` project in this topic folder, neither of them checked in.

## Beats

### Beat 1: installing a skill adds a folder and changes nothing else (1 min)

**Open:** [Step 1: Install the Skill](demo-docx-invoice.md#step-1-install-the-skill) · [`readme.md`](readme.md) · `.claude/skills/<skill-name>/` (created by the install)
**Say:** Adopting a skill is a smaller commitment than the word install suggests, and deleting the directory is the entire uninstall. Confirm it by reading the folder.

```text
Before installing the skill you found in Step 1, read demos/03-skills/01-intro/readme.md and answer these questions:

1. Where does the skill folder land after installation?
2. What is the minimum file required inside a skill folder?
3. Does installing a skill change settings.json or CLAUDE.md?

One sentence per answer.
```

**Result:** nothing outside the folder moves; this repo's [`.claude/settings.json`](../../../.claude/settings.json) carries one hooks block and names none of the folders under `.claude/skills/`

```json
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/delegation-reminder.sh\"",
```

**Gotcha:** `SKILL.md` is the only required file and the name is case-sensitive, so a lowercase `skill.md` works on a laptop and disappears in CI.

### Beat 2: read what you just installed, because `description` is the whole trigger (1 min)

**Open:** [`readme.md`](readme.md#skill-anatomy) · `.claude/skills/<skill-name>/SKILL.md` (created by the install in Step 1)
**Say:** An installed skill runs in your sessions without anyone invoking it by name. Read the frontmatter that actually landed on disk, and count the fields.

```text
Install the DOCX skill you identified in Step 1 by copying its skill folder into .claude/skills/.
After installation, read the SKILL.md file that was installed and list:
- The skill name
- All trigger phrases
- All tools in the allowlist
Do not create any TypeScript files yet.
```

**Result:** the same read-back against a skill already installed here, [`code-reviewer/SKILL.md`](../../../.claude/skills/code-reviewer/SKILL.md), two fields and no `tools` array at all

```yaml
---
name: code-reviewer
description: Use this skill to review code. It supports both local changes (staged or working tree) and remote Pull Requests (by ID or URL). It focuses on correctness, maintainability, and adherence to project standards.
---
```

**Gotcha:** there is no separate trigger list and no `tools` array here; `description` is what the model matches against, and an absent allowlist means the skill inherits whatever the session can already do. [Module 3: 02 Creating](../02-creating/readme.md) has the full field reference.

### Beat 3: the requirements list is what makes the output checkable (2 min)

**Open:** [Step 2: Generate a TypeScript Invoice](demo-docx-invoice.md#step-2-generate-a-typescript-invoice) · the Requirements list in the Recipe · [`readme.md`](readme.md)
**Say:** "It ran without errors" is not a definition of done. A requirements list earns its place by naming things anyone can check without judgement.

```text
Requirements:
- Use TypeScript with strict mode enabled
- Create package.json with a "build" script that compiles TypeScript and a "generate" script that runs the output
- Create tsconfig.json targeting ES2020 with moduleResolution set to node
- Write the invoice to invoice.docx in the same folder
- Install the docx package, typescript@5 and ts-node as devDependencies
- Do not add inline comments to the TypeScript source
```

**Result:** an `invoice/` tree in this topic folder, none of it checked in: `package.json`, `tsconfig.json`, the TypeScript source, and `invoice.docx`, which is the only one checkable without reading the source

**Gotcha:** every line is an assertion someone can check without opening Word, so "it worked" means a specific document that a reader can open.

## If the room asks

| Question | Answer |
|---|---|
| Why not just ask for the code directly and skip the skill? | You can, and you then supply the domain contract yourself; the skill exists so the `Document`, `TextRun` and `Packer` chain is known before the first line. |
| Is a skill just a bigger slash command? | It is a folder, so it can carry references and scripts, and it is installed on its own, separately from the project's commits; module 3 adds running one in a forked subagent. |
