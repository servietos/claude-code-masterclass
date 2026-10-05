---
presents: demo-docx-invoice.md
budget: 4 min
beats: 4
---

# Present: Use a DOCX Skill to create an Invoice Generator

A skill searched for, installed, and then left to drive a TypeScript invoice generator. A room walks away knowing that installing a skill only drops a folder, and that its value is the domain contract handed over before any code exists.

------

This topic ships no `-solution` folder: the run leaves an installed skill folder under [`.claude/skills/`](../../../.claude/skills) at the repo root and a generated `invoice/` project in this topic folder, neither of them checked in.

## Beats

### Beat 1: installing a skill adds a folder and changes nothing else (1 min)

**Open:** [Step 2: Install the Skill](demo-docx-invoice.md#step-2-install-the-skill) · the three questions in the Research prompt · [`readme.md`](readme.md) · `.claude/skills/<skill-name>/` (created by the install)
**Say:** Adopting a skill is a smaller commitment than the word install suggests, and deleting the directory is the entire uninstall. Confirm it rather than assume it.

```text
Before installing the skill you found in Step 1, read demos/02-harness/04-skills/readme.md and answer these questions:

1. Where does the skill folder land after installation?
2. What is the minimum file required inside a skill folder?
3. Does installing a skill change settings.json or CLAUDE.md?

One sentence per answer.
```

**Result:** nothing outside the folder moves; this repo's [`.claude/settings.json`](../../../.claude/settings.json) carries one hooks block and names none of its eleven skill folders

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

**Open:** [`readme.md`](readme.md#what-are-skills) · `.claude/skills/<skill-name>/SKILL.md` (created by the install in Step 2)
**Say:** An installed skill runs in your sessions without anyone invoking it by name. Read the frontmatter that actually landed on disk rather than the one you pictured, and count the fields.

```text
Install the DOCX skill you identified in Step 1 using the claude skills install command.
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

**Gotcha:** there is no separate trigger list and no `tools` array here; `description` is what the model matches against, and an absent allowlist means the skill inherits whatever the session can already do. [Module 3: 02 Creating](../../03-skills/02-creating/readme.md) has the full field reference.

### Beat 3: the skill's real payload is a domain contract, and `Packer` is where it is usually dropped (1 min)

**Open:** [Step 3: Generate a TypeScript Invoice](demo-docx-invoice.md#step-3-generate-a-typescript-invoice) · the Research prompt on the docx API · [`readme.md`](readme.md)
**Say:** What a good skill supplies is the objects a library expects, in the order it expects them, known before the first line is written. Ask about the step that is easy to omit before any code exists.

```text
The docx npm package is the most popular TypeScript library for generating Word documents programmatically.
Before writing any code, explain:

1. What top-level object does the docx package use to represent a document?
2. How are paragraphs and text runs structured in the docx API?
3. How is the final .docx file written to disk using the Packer class?

Keep each answer to two sentences. Do not generate any code yet.
```

**Result:** nothing on disk, by design: this beat ends in an explanation, and `invoice.docx` in Beat 4 is the only artifact that ever proves `Packer.toBuffer` ran

**Gotcha:** question 3 is the trip-up, because a program that builds a perfect `Document` and never packs it runs clean, exits 0, and writes no file.

### Beat 4: the requirements list is what makes the output checkable (1 min)

**Open:** [Step 3: Generate a TypeScript Invoice](demo-docx-invoice.md#step-3-generate-a-typescript-invoice) · the Requirements list in the Recipe · [`readme.md`](readme.md)
**Say:** "It ran without errors" is not a definition of done. A requirements list earns its place by naming things anyone can check without judgement.

```text
Requirements:
- Use TypeScript with strict mode enabled
- Create package.json with a "build" script that compiles TypeScript and a "generate" script that runs the output
- Create tsconfig.json targeting ES2020 with moduleResolution set to node
- Write the invoice to invoice.docx in the same folder
- Install the docx package and ts-node as devDependencies
- Do not add inline comments to the TypeScript source
```

**Result:** an `invoice/` tree in this topic folder, none of it checked in: `package.json`, `tsconfig.json`, the TypeScript source, and `invoice.docx`, which is the only one checkable without reading the source

**Gotcha:** every line is an assertion someone can check without opening Word, so "it worked" means a specific document rather than a plausible one.

## If the room asks

| Question | Answer |
|---|---|
| `/find-skills` returned several DOCX skills. Which one? | The one that fits a TypeScript project using the `docx` npm package; ask for name, description, allowed-tools and whether it bundles references or scripts, then choose on that. |
| Why not just ask for the code directly and skip the skill? | You can, and you then supply the domain contract yourself; the skill exists so the `Document`, `TextRun` and `Packer` chain is known before the first line. |
| Is a skill just a bigger slash command? | It is a folder, so it can carry references and scripts, and it is installed independently instead of committed with the project; module 3 adds running one in a forked subagent. |
