# Use a DOCX Skill to create an Invoice Generator

A skill is a folder of domain instructions the model loads on trigger, and installing one changes nothing else in the project. You search the skill catalog for a Word-document skill, install it, read what it actually added, and let it drive the code you ask for. You finish with the skill folder in place and a TypeScript program that renders a sample invoice as a `.docx` file.

---

## Setup

Open Claude Code in this repository. No additional dependencies need to be installed before you begin.

---

## Step 1: Find a DOCX Skill

**Overview:** Skills extend Claude Code with domain-specific workflows. Before installing anything, use the skill catalog to understand what document-generation skills exist and how they differ.

**Research / Planning / Discussion:**

```text
Use /find-skills to search for skills related to generating Word documents or DOCX files.
List the skills you find, what each one does, and what triggers activate it.
Do not install anything yet.
```

**Finding:** Claude should return at least one skill with `docx` or `word-document` in the name or description, list its trigger phrases, and mention whether it bundles references or scripts. If Claude returns more than one option, push back and ask which one best fits a TypeScript project that uses the `docx` npm package.

**Recipe:**

```text
Run /find-skills with the query "create docx" or "word document".
For each result, list: skill name, one-sentence description, the description text the model matches on, and whether it bundles references or scripts.
Recommend the best skill for a TypeScript invoice generator and explain why in one sentence.
```

**Expected Outcome:** A short table or list showing at least one installable DOCX skill with its name, trigger phrases, and a recommendation with reasoning.

---

## Step 2: Install the Skill

**Overview:** Installing a skill copies its folder into `.claude/skills/` so Claude can trigger it automatically whenever a matching phrase appears in your prompts.

**Research / Planning / Discussion:**

```text
Before installing the skill you found in Step 1, read demos/02-harness/04-skills/readme.md and answer these questions:

1. Where does the skill folder land after installation?
2. What is the minimum file required inside a skill folder?
3. Does installing a skill change settings.json or CLAUDE.md?

One sentence per answer.
```

**Finding:** Claude should confirm that the skill lands in `.claude/skills/<skill-name>/`, that `SKILL.md` is the only required file, and that installation does not touch `settings.json` or `CLAUDE.md`. If it says installation modifies either file automatically, push back and ask it to re-read the readme.

**Recipe:**

```text
Install the DOCX skill you identified in Step 1 using the claude skills install command.
After installation, read the SKILL.md file that was installed and list:
- The skill name
- All trigger phrases
- All tools in the allowlist
Do not create any TypeScript files yet.
```

**Expected Outcome:** A `.claude/skills/<skill-name>/SKILL.md` file exists in the repository. The trigger phrases and tool allowlist are printed in the response.

---

## Step 3: Generate a TypeScript Invoice

**Overview:** With the skill installed, use its trigger phrase to activate the skill and produce a TypeScript program that creates a sample invoice as a `.docx` file using the `docx` npm package.

**Research / Planning / Discussion:**

```text
The docx npm package is the most popular TypeScript library for generating Word documents programmatically.
Before writing any code, explain:

1. What top-level object does the docx package use to represent a document?
2. How are paragraphs and text runs structured in the docx API?
3. How is the final .docx file written to disk using the Packer class?

Keep each answer to two sentences. Do not generate any code yet.
```

**Finding:** Claude should explain that `Document` is the root object, that paragraphs contain `Paragraph` objects with `TextRun` children that carry text and formatting, and that `Packer.toBuffer(doc)` returns a promise resolving to a `Buffer` that can be written with `fs.writeFile`. If the explanation is vague or skips the `Packer` step, ask it to look up the docx npm package docs before continuing.

**Recipe:**

```text
Create a TypeScript project at demos/02-harness/04-skills/invoice/ that generates a sample invoice as a .docx file using the docx npm package.

The invoice must include:
- A title: "INVOICE"
- Invoice number: INV-2024-001
- Date: 2024-01-15
- Bill To section with a fictional company name and address
- A line-item table with columns: Description, Quantity, Unit Price, Total
- Three line items of your choice
- A subtotal, VAT (20%), and grand total row
- A footer: "Payment due within 30 days"

Requirements:
- Use TypeScript with strict mode enabled
- Create package.json with a "build" script that compiles TypeScript and a "generate" script that runs the output
- Create tsconfig.json targeting ES2020 with moduleResolution set to node
- Write the invoice to invoice.docx in the same folder
- Install the docx package and ts-node as devDependencies
- Do not add inline comments to the TypeScript source

After creating all files, run npm install and npm run generate to produce invoice.docx.
```

**Expected Outcome:** A folder at `demos/02-harness/04-skills/invoice/` containing `package.json`, `tsconfig.json`, a TypeScript source file, and `invoice.docx`. Running `npm run generate` from that folder produces the `.docx` file without errors.

