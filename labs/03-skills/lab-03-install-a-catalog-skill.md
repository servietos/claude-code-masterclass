# Install a Catalog Skill and Let It Shape Real Code

You need a Word document from a program, and the model has no standing knowledge of how your team builds one. A catalog skill carries that knowledge, but installing something blind leaves you guessing what it adds and when it fires. You finish with a DOCX skill you chose, verified and installed into this lab's own `.claude/skills/`, plus a TypeScript program it shaped that writes a delivery note as a `.docx` file.

What you practice here: find a skill, read what an install changes, and prove the skill drives the code.

Duration: about 40 minutes.

------

Each step follows the same pattern:

- **Overview**: what this step achieves
- **Research / Planning / Discussion**: an open prompt to reason through the problem before acting
- **Finding**: what to read and evaluate in Claude's response before moving on
- **Recipe**: a complete implementation prompt you can use as-is or adapt from your own findings
- **Expected Outcome**: observable artefacts that confirm success

Work in the pristine starter [catalog-skill/](catalog-skill). The concepts live in [Topic 01](../../demos/03-skills/01-intro/readme.md); the lab applies them and leaves the explanation there.

---

## Where to Open Claude Code

The install writes `.claude/skills/` into the directory the session was launched in, and Claude loads project skills from that same directory. Open Claude Code inside the lab folder so the skill lands next to the code it will shape. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/03-skills/catalog-skill
claude
```

If you start Claude Code with the Claude Terminal extension, it opens in the VS Code workspace folder. Open `catalog-skill` as the workspace folder (File > Open Folder) before pressing the shortcut, or run the commands above in a plain terminal.

Every path below is relative to `labs/03-skills/catalog-skill/`.

---

## Setup

Install the dependencies and look at the data the program will turn into a document:

```bash
npm install
```

`data/delivery.json` holds one delivery note: a supplier, a recipient, three items with quantities and units, and a remark for the driver. `scripts/inspect-docx.mjs` reads a `.docx` back and prints its table count and text, so you can check a document without opening Word. Nothing renders the data yet; the skill shapes that code in Step 5.

---

## Step 1: Find a DOCX Skill in the Catalog

**Overview:** The Skills CLI searches the public catalog at skills.sh by keyword and prints every hit as `owner/repo@skill` with its install count. Searching first shows you the candidates before anything touches your disk.

**Research / Planning / Discussion:**

```text
Run npx -y skills@1.7.2 find docx and show me the output. For every hit that works
with Word documents, give me the source repository, the install command and the
install count. Which one would you pick to generate a .docx from a TypeScript
program, and why?
```

**Finding:** Every hit in the answer should appear in the search output with its `https://skills.sh/...` link, and the install command follows the form the CLI prints at the top, `npx skills add <owner/repo@skill>`. `anthropics/skills@docx` is the hit that creates `.docx` files; the Lark and WeCom hits work with those platforms' online documents. If Claude names a skill that is not in the output, ask where it came from. Install counts change daily, so your numbers differ from a neighbour's.

**Recipe:**

```text
Run npx -y skills@1.7.2 find docx, then npx -y skills@1.7.2 add anthropics/skills --list
to read the skill descriptions without installing anything. Show every hit that works
with Word documents as a table with the columns Skill, Source, Install command and
Installs. Then recommend one for generating a .docx from TypeScript with the docx npm
package, in two sentences.
```

**Expected Outcome:** A table of at least two Word-related hits that includes `anthropics/skills@docx` with the install command `npx skills add anthropics/skills@docx`, and a recommendation for `docx`. `.claude/skills/` does not exist yet in `catalog-skill/`.

---

## Step 2: Confirm What an Install Changes Before You Run It

**Overview:** An install is a change to your project. Reading the readme first turns "it should be fine" into predictions you can check against the disk.

**Research / Planning / Discussion:**

```text
Read ../../../demos/03-skills/01-intro/readme.md, section "What an Install Changes".
Before we install anything, predict for the DOCX skill you recommended:

1. Which folder will appear, and what is the minimum file inside it?
2. Will settings.json or CLAUDE.md change?
3. How would I undo the install completely?

One sentence per answer, and list the files you expect to see afterwards.
```

**Finding:** The predictions should say one new folder under `.claude/skills/` containing at least a `SKILL.md` (exact case), no change to `settings.json` or `CLAUDE.md`, and an uninstall that deletes that folder. Keep the file list: Step 3 checks it against the disk. Push back if Claude predicts a settings entry or a plugin registration.

**Recipe:**

```text
Read ../../../demos/03-skills/01-intro/readme.md, section "What an Install Changes",
and answer in a table with the columns Question and Answer:
1. Where does the skill folder land?
2. What is the minimum file in it?
3. Does an install touch settings.json or CLAUDE.md?
4. How do I uninstall?
Then list the files you expect in the installed skill folder.
```

**Expected Outcome:** A four-row table whose answers match the readme, plus a predicted file list that you keep for the next step. `.claude/skills/` is still absent.

---

## Step 3: Install the Skill Into This Lab

**Overview:** The Skills CLI installs into the current folder's `.claude/skills/` unless you pass `-g`. Naming the agent and the skill keeps the command free of prompts, so Claude can run it for you; then you compare the disk with your prediction.

**Research / Planning / Discussion:**

```text
I want the docx skill from Step 1 in .claude/skills/ of this folder and nowhere in my
home directory. Read the output of npx -y skills@1.7.2 --help and tell me which flags
make the install project-scoped, free of prompts, a plain copy, and for Claude Code
only. Give me the full command before running anything.
```

**Finding:** The answer should land on `-a claude-code` (only Claude Code's skill folder), `-y` (no confirmation prompts), `--copy` (a real folder, where the default symlink can fail on Windows) and no `-g`, because `-g` installs into `~/.claude/skills/`. Reject a command without `-a`: with `-y` the CLI installs for every agent it supports, and folders such as `.agents/skills/` appear beside `.claude/skills/`.

**Recipe:**

```text
Run npx -y skills@1.7.2 add anthropics/skills@docx -a claude-code -y --copy in this
folder. After the install:
1. Run git status and show me every changed or new path.
2. Confirm settings.json and CLAUDE.md are untouched.
3. List the files inside .claude/skills/docx/ and print skills-lock.json.
Do not create any TypeScript files yet.
```

Check the result yourself in a second terminal:

```bash
find .claude/skills -maxdepth 3
```

```powershell
Get-ChildItem .claude\skills -Recurse -Depth 2 | Select-Object FullName
```

**Expected Outcome:** `.claude/skills/docx/` holds `SKILL.md`, `LICENSE.txt` and a `scripts/` folder, and `git status` lists two new paths: `.claude/` and `skills-lock.json`. The lockfile records the source `anthropics/skills`, the skill path and a content hash; it is the one file the readme's folder-copy model does not predict, and `npx skills experimental_install` restores skills from it. No settings or `CLAUDE.md` file changed, and nothing under `~/.claude/skills/` changed.

---

## Step 4: Read Back What the Skill Promises

**Overview:** The frontmatter decides when the skill fires and what it may do without asking. Reading it back tells you what you installed.

**Research / Planning / Discussion:**

```text
Read .claude/skills/docx/SKILL.md.
Quote the description field and list the trigger phrases it contains. Then tell me:

1. Which prompts from my work would fire this skill, and which Word-related prompts
   would it miss?
2. Does the file contain an allowed-tools line, and what would each entry let through
   without a permission prompt?
3. Is there anything in the body I should check before I let it run commands?
```

**Finding:** Look for verbatim quotes from the file. A skill with no `allowed-tools` line pre-approves nothing, and every tool follows your normal permission flow; a listed tool runs without a prompt for the turn that invokes the skill. The `docx` skill has no `allowed-tools` line, so it pre-approves nothing; its body tells Claude to run Python scripts from its own `scripts/` folder when it edits, converts or comments on an existing document, while creating a new file goes through the `docx` npm package. If Claude paraphrases, ask for the exact lines.

**Recipe:**

```text
Read .claude/skills/docx/SKILL.md. Print:
- name
- description, verbatim
- trigger phrases, one per line
- every entry of allowed-tools, with one sentence on what it lets through
- the names of any files the body tells Claude to load or run
Do not change any file.
```

**Expected Outcome:** A printed summary with the name `docx`, the description starting `Use this skill whenever the user wants to create, read, edit, or manipulate Word documents`, trigger phrases such as `Word doc`, `.docx` and `report`, a statement that no `allowed-tools` line exists, and the scripts the body names under `scripts/`. Compare the trigger phrases with the request you send in Step 5.

---

## Step 5: Let the Skill Shape a Delivery-Note Generator

**Overview:** The proof of a skill is that the code it produces follows its guidance. The Research prompt checks that the description matches your plain words; the Recipe types `/docx` so the skill loads whichever model you run, and the code shows whether its guidance arrived.

**Research / Planning / Discussion:**

```text
I want a TypeScript program in src/delivery-note.ts that reads data/delivery.json and
writes out/delivery-note.docx. Before writing anything, tell me which installed skill
would apply to this request, which of its instructions will change how you write the
code, and what you would verify afterwards.
```

**Finding:** Claude should name the DOCX skill, point at specific instructions in its `SKILL.md`, and propose checking the generated file itself. If it plans to write the program without mentioning the skill, the description did not match; reword the request with a trigger phrase from Step 4 or type `/docx` to invoke it explicitly.

**Recipe:**

```text
/docx Create a Word delivery note generator in TypeScript, strict mode, using the docx package.

- Read data/delivery.json and write out/delivery-note.docx (create out/ if missing)
- Title "DELIVERY NOTE" with the note number and date
- Supplier and recipient blocks, including the contact person
- A table with the columns SKU, Description, Quantity, Unit and one row per item,
  with a bold header row
- A total quantity row for the pieces, and the remarks as a closing paragraph
- Source in src/delivery-note.ts, no inline comments
- The package.json scripts "build" and "generate" already exist; use them

Run npm run build, npm run generate and npm run inspect, and show me the output of
the inspect command.
```

**Expected Outcome:** `src/delivery-note.ts` exists and follows the skill's table rules: `columnWidths` on the table and a `WidthType.DXA` width on every cell, with `ShadingType.CLEAR` wherever it shades the header row. `out/delivery-note.docx` is on disk. `npm run inspect` prints `tables: 1` and a text list that contains `DN-2026-0142`, `AL-2040`, `FX-M8`, `CT-RAL` and the piece total of 600.

The file on disk is the receipt. A program that builds a perfect `Document` and never calls `Packer.toBuffer` exits cleanly and writes nothing, so check `out/` before you believe the summary.

> Conversation branch: if you worked through the Research conversation, continue with what it produced. The Recipe is a reference prompt for readers who skipped the conversation or start fresh; where its assumptions differ from your findings, your findings win.

---

## Verify

Run the whole chain once more to confirm that the skill, the program and the document agree:

```bash
npm run build && npm run generate && npm run inspect
```

The command ends with the inspect output and no error. To undo the lab, delete `.claude/skills/docx/`, `skills-lock.json`, `src/`, `dist/` and `out/`; the starter files stay as they were.
