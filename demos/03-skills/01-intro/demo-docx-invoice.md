# Use a DOCX Skill to create an Invoice Generator

A skill is a folder of domain instructions the model loads on trigger, and installing one changes nothing else in the project. You search the skill catalog for a Word-document skill, install it, read what it actually added, and let it drive the code you ask for.

---

## Step 1: Install the Skill

Start Claude Code from the repository root, where the install writes `.claude/skills/`, and pick a DOCX skill with `/find-skills`. Confirm what an install touches, then copy the skill folder in so Claude can trigger it on matching prompts.

```text
Before installing the skill you found in Step 1, read demos/03-skills/01-intro/readme.md and answer these questions:

1. Where does the skill folder land after installation?
2. What is the minimum file required inside a skill folder?
3. Does installing a skill change settings.json or CLAUDE.md?

One sentence per answer.
```

```text
Install the DOCX skill you identified in Step 1 by copying its skill folder into .claude/skills/.
After installation, read the SKILL.md file that was installed and list:
- The skill name
- All trigger phrases
- All tools in the allowlist
Do not create any TypeScript files yet.
```

**Expected Outcome:** A `.claude/skills/<skill-name>/SKILL.md` file exists in the repository. The trigger phrases and tool allowlist are printed in the response.

The install adds one folder and touches neither `settings.json` nor `CLAUDE.md`; if Claude says it does, push back and ask it to re-read the readme.

## Step 2: Generate a TypeScript Invoice

With the skill installed, use its trigger phrase to activate the skill and produce a TypeScript program that creates a sample invoice as a `.docx` file using the `docx` npm package.

```text
Create a TypeScript project at demos/03-skills/01-intro/invoice/ that generates a sample invoice as a .docx file using the docx npm package.

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
- Install the docx package, typescript@5 and ts-node as devDependencies
- Do not add inline comments to the TypeScript source

After creating all files, run npm install, npm run build and npm run generate to produce invoice.docx.
```

**Expected Outcome:** A folder at `demos/03-skills/01-intro/invoice/` containing `package.json`, `tsconfig.json`, a TypeScript source file, and `invoice.docx`. Running `npm run build` and then `npm run generate` from that folder produces the `.docx` file without errors.

`invoice.docx` on disk is the only proof that `Packer.toBuffer` ran: a program that builds a perfect `Document` and never packs it exits 0 and writes no file.
