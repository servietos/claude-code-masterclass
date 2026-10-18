# Package Invoice Generation Into a Skill Claude Fires on Its Own

Turn a one-off document script into a composite skill: frontmatter that makes it trigger, a reference file that holds the layout contract, a script that owns the rendering, pre-approved tools, and a live value injected at load time. You finish with a skill that answers "invoice Nordwind for two days of training" with a real Word document.

Each step follows the same pattern:

- **Overview**: what this step achieves
- **Research / Planning / Discussion**: an open prompt to reason through the problem before acting
- **Finding**: what to read and evaluate in Claude's response before moving on
- **Recipe**: a complete implementation prompt you can use as-is or adapt from your own findings
- **Expected Outcome**: observable artefacts that confirm success

The completed reference lives in [invoice-skill-solution/](invoice-skill-solution). Work in the pristine starter [invoice-skill/](invoice-skill) and open the solution only when you want to compare.

---

## Where to Open Claude Code

This lab builds a project-scoped skill, so open Claude Code inside the lab folder. `.claude/skills/` loads from the directory the session was launched in, and a session opened at the repo root leaves everything you write here inert with no error to tell you.

The starter is already in this repo, so there is nothing to scaffold: change into it and start the session there. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/03-skills/invoice-skill
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `invoice-skill` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the command above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere in the repo:

```text
In labs/03-skills/invoice-skill write the scope document for an invoice-docx skill ....
```

That works for any step whose result is just files, such as the scope document in Step 1 and the reference and renderer in Step 3. It does not work for the skill itself: `.claude/skills/invoice-docx/` loads from the directory the session was launched in, so a root session writes the skill into the lab folder and then ignores it, and neither the load-time injection in Step 4 nor the trigger test in Step 5 can fire. Launch inside the starter from Step 1 onward.

Launching inside the starter is what makes the repository a monorepo to this lab, with the starter as the project: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session and are read from the repo root. You read from them without ever writing into them, and every path in the prompts below is relative to the lab folder.

Every `.claude/skills/invoice-docx/` path below is relative to `labs/03-skills/invoice-skill/`.

---

## Setup

Install the one dependency and look at the data you will be rendering:

```bash
npm install
```

`data/invoice-sample.json` carries a realistic Austrian invoice: two parties with VAT IDs, three line items, and a 20% rate expressed as `"taxRate": 0.2`. Nothing renders it yet; that is what you build.

Step 1 narrows the new skill against two general document skills: `docx` (general-purpose reading, editing, tracked changes, find-and-replace) and `create-docx` (programmatic generation via docx-js). Neither ships with Claude Code; install a DOCX skill from the catalog with `/find-skills`, the way [Topic 01](../../demos/03-skills/01-intro/readme.md) does, and list what you have with `/skills`.

---

## Step 1: Draw the Scope Line Against the General Document Skills

**Overview:** A skill earns its place by being narrower than what already exists. Before writing a line of it, establish what an invoice skill knows that a general document skill cannot.

**Research / Planning / Discussion:**

```text
Two document skills are already available to you: docx (general Word manipulation) and
create-docx (programmatic generation with docx-js). I want a third skill that generates
invoices for my company.

1. What does an invoice-specific skill know that neither of those two knows?
2. Which parts of invoice generation are document mechanics (already covered) and which
   are domain rules (mine to encode)?
3. Where should the arithmetic live: in the skill's instructions, or in a script the
   skill calls? Argue both sides, then recommend one.
```

**Finding:** A strong answer separates document mechanics (tables, bold runs, page setup, which the general document skills cover) from domain rules (which fields an invoice must carry, VAT as a fraction, net versus gross, due-date defaults, that a missing VAT ID is a question for the user). On the third question it should land on the script: a model that recomputes totals in prose will eventually produce a document and a reply that disagree, and only one of them is the invoice. If the answer wants the arithmetic in `SKILL.md`, push back with that failure case.

**Recipe:**

```text
Write a scope document for a skill named invoice-docx, under 40 lines, with these sections:
- Purpose (one sentence)
- In scope (the domain rules the skill owns)
- Out of scope (what docx and create-docx already cover, and what the skill must refuse)
- Trigger phrases (four realistic user requests, in quotes)
- Inputs the skill must collect before rendering, marking which ones it may default and
  which it must ask for
```

**Expected Outcome:** A scope document whose In-scope list is about invoices and leaves Word mechanics to the Out-of-scope list. The trigger phrases are things a person actually types, such as "invoice Nordwind for two days of training".

---

## Step 2: Write the Skill and Pre-Approve Its Tools

**Overview:** Author `SKILL.md` with frontmatter that triggers reliably and an `allowed-tools` line that pre-approves the three tools the skill runs, so a triggered invoice does not stall on permission prompts.

**Research / Planning / Discussion:**

```text
For the invoice-docx skill, propose the frontmatter:

1. A description field that fires on my four trigger phrases and does NOT fire on
   "read this contract.docx" or "fix the formatting in report.docx".
2. An allowed-tools value. The skill needs to read data, write a JSON file and a document,
   and run a Node script. What is the minimum set, and what does each entry let through?
3. Explain the difference between a skill that lists allowed-tools and one that does not,
   in terms of what the session can do while the skill is active. Which frontmatter field
   takes a tool away?
```

**Finding:** The description should carry the trigger phrases verbatim and an explicit exclusion, because a description that only says what the skill does will also match every other Word request. On tools, `Read, Write, Bash(node:*)` is the honest minimum; watch for an answer that adds `Bash(*)` or `Edit` without justifying them, because every entry runs without a prompt. The third answer should be clear that `allowed-tools` is a pre-approval: the listed tools run without a permission prompt for the turn that invokes the skill, every other tool stays callable under your normal permission rules, and only `disallowed-tools` takes a tool away while the skill is active. Push back if Claude describes `allowed-tools` as a sandbox.

**Recipe:**

```text
Create .claude/skills/invoice-docx/SKILL.md with:
- Frontmatter: name invoice-docx, the description from the research step, and
  allowed-tools "Read, Write, Bash(node:*)"
- An Inputs table: field, notes, and which fields may be defaulted
- A Steps section: write the collected data to data/<number>.json, run the renderer,
  then report the output path and the totals the renderer computed
- Examples and Troubleshooting sections

The skill must never recompute totals in its reply; the renderer is the single source of
those numbers. State that explicitly in the file.
```

**Expected Outcome:** `.claude/skills/invoice-docx/SKILL.md` exists with valid YAML frontmatter, an `allowed-tools` line naming three tools, and a Steps section that delegates the arithmetic. `/skills` lists `invoice-docx`.

---

## Step 3: Split the Layout Into a Reference and the Rendering Into a Script

**Overview:** A skill that inlines its data shape and its rendering code is slow to load and hard to change. Move the contract into `references/` and the implementation into `scripts/`, leaving `SKILL.md` to hold decisions.

**Research / Planning / Discussion:**

```text
Read the SKILL.md I just wrote. For each block in it, say whether it belongs in SKILL.md,
in references/, or in scripts/, and justify the move on two grounds: is it long enough to
bloat the file Claude loads on every trigger, and is it static enough that it does not get
rewritten per invoice?

Then: what exactly should a reference file for this skill contain, given that a script
does the rendering and the model only supplies the data?
```

**Finding:** The data shape, the block-by-block document layout, and the arithmetic rules are static and belong in `references/`. Decision points (what to ask for, what may be defaulted, when to refuse) stay in `SKILL.md`. The useful insight for the second question is that the reference is the contract between the model and the script: the model writes JSON, the script consumes it, and the reference is what keeps them agreeing.

**Recipe:**

```text
Refactor .claude/skills/invoice-docx/:

1. Create references/invoice-layout.md with the JSON data shape (a full example),
   a table of the document blocks in order, and the arithmetic rules
   (amount per line, net, VAT, gross, and the currency formatting).
2. Create scripts/render.mjs using the docx package:
   - Read a JSON path and an output path from argv
   - Build the document per references/invoice-layout.md: Heading 1, issue and due line,
     seller block, buyer block, a four-column table with a bold header row and
     right-aligned numeric columns, then right-aligned Net, VAT and Total with Total bold
   - Export the document builder as a function as well, so it can be reused later
3. Trim SKILL.md so it links to the reference and no longer restates the layout.

Then render the sample: node .claude/skills/invoice-docx/scripts/render.mjs \
  data/invoice-sample.json out/invoice-sample.docx
```

**Expected Outcome:** The skill folder holds `SKILL.md`, `references/invoice-layout.md` and `scripts/render.mjs`. `out/invoice-sample.docx` opens in Word with the three line items, and the totals read `EUR 8850.00`, `EUR 1770.00` and `EUR 10620.00`. `SKILL.md` is visibly shorter than after Step 2.

---

## Step 4: Inject a Live Value at Load Time

**Overview:** A skill body is static text unless you inject into it. The issue date is the natural candidate: it changes every day and the model has no reliable way to know it.

**Research / Planning / Discussion:**

```text
My invoice skill defaults the issue date to today. Right now nothing tells it what today is.

1. What does the `` !`command` `` syntax in a SKILL.md body do, and at what moment does it run?
2. Why is a shell command a better source for today's date than the model's own answer?
3. What would go wrong if I injected the entire data/ directory listing this way instead?
```

**Finding:** The answer should be precise that the backtick-bang block runs when the skill is loaded and its stdout is substituted into the body before the model reads it, which is what makes it current on every load. On the third question, look for the cost argument: injection happens on every trigger, so a large or slow command is paid for every time, and directory listings grow without bound.

**Recipe:**

```text
Add a line near the top of the SKILL.md body that injects today's date with
`` !`date +%Y-%m-%d` `` and states that this is the issue date unless the user names
another one. Keep it to one line.

Then verify the injection: start a fresh session, trigger the skill, and have it tell me
which date it will put on the invoice without rendering anything.
```

**Expected Outcome:** The skill reports the real current date, the one `date` printed when the skill loaded. Editing the line to an invalid command and re-triggering shows the failure surfacing at load time, which is worth seeing once.

---

## Step 5: Prove It Triggers, Then Bill a Real Customer

**Overview:** A skill nobody triggers is a file. Test the description against prompts that should and should not fire it, then run the whole thing end to end from a plain-English request.

**Research / Planning / Discussion:**

```text
Read .claude/skills/invoice-docx/SKILL.md and predict, for each prompt below, whether the
description would trigger the skill. Explain each prediction from the wording of the
description, then say which prompt is the riskiest and why.

Should trigger:
1. "Invoice Nordwind for two days of training at 3200 a day."
2. "Bill Salzburg Logistics for 8 support hours at my usual rate."
Should not trigger:
3. "Read contract.docx and summarise the payment terms."
4. "Fix the heading styles in report.docx."
```

**Finding:** Prompt 2 is the interesting one: it fires the skill but is missing the rate and the buyer's VAT ID, so the right behaviour is to ask for both before rendering. If the prediction says the skill would happily invent a rate, tighten the Inputs table before continuing.

**Recipe:**

```text
Invoice Nordwind Handels GmbH for two days of the Claude Code masterclass at 3200 per day
and 8 hours of follow-up support at 125 per hour. Use my details from
data/invoice-sample.json as the seller. 20% VAT, payable in 14 days.
```

**Expected Outcome:** Claude triggers `invoice-docx` without being told to, writes a new JSON file under `data/`, runs the renderer, and reports the output path with net, VAT and gross taken from the script's output. The document opens in Word and the totals match the JSON. Ask for the same invoice at 10% VAT and only the JSON and the document change; the skill stays as it is.
