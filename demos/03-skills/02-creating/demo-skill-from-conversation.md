# Create a Skill from a Proven Claude Code Chat

Prompt Claude to build a JavaScript sales-revenue calculator, then extract the decision sequence that conversation proved into a reusable skill. You end with a working `sales-by-region.js` module and a `data-aggregator` SKILL.md whose workflow and constraints replay that same sequence on any new aggregation task.

------

## Setup

Work in this topic's starter, which ships empty because every artifact here is one you prompt Claude to write:

```bash
cd demos/03-skills/02-creating/skill-from-conversation
claude
```

Everything you create is untracked, so the Cleanup section at the end removes it with git. If you only want the finished result, read [skill-from-conversation-solution](skill-from-conversation-solution/readme.md).

---

## Step 1: Build the Sales Revenue Module

**Overview:** Produce a working JavaScript module through prompting. This conversation becomes the raw material for skill extraction: the workflow Claude follows, the decisions it makes, and the structure it produces.

**Research / Planning / Discussion:**

```text
I need a JavaScript module that aggregates sales data by region. Before writing any code, walk me through the design:

- What should the input look like (field names, types)?
- What should the output structure be?
- What edge cases matter for a financial aggregation?

Do not write code yet. Just explain the design.
```

**Finding:** Claude should propose a clear input schema (an array of objects with at minimum region and amount fields), explain the output structure (an array or object keyed by region), and name at least two edge cases: missing fields and zero-value entries. If Claude jumps directly to code, redirect: "Describe the data contract before implementing."

**Recipe:**

```text
Build a JavaScript module called sales-by-region.js that exports two functions:

salesByRegion(records)
- Input: array of objects with region (string), product (string), and amount (number)
- Output: array of { region, total } objects sorted by total descending

formatReport(results)
- Input: the output of salesByRegion
- Output: a formatted string with one line per region: "Region: <name>  Revenue: $<total>"

Use CommonJS (module.exports) so the file runs with node sales-by-region.js without a package.json.

At the bottom of the file, add a sample dataset of 8 records spanning 3 regions, then call both functions and log the result inside an if (require.main === module) guard, so the file can be run directly with node sales-by-region.js and stays silent when another module imports it.

No dependencies. No inline comments.
```

**Expected Outcome:** A file `sales-by-region.js` that runs with `node sales-by-region.js` and prints a region-sorted revenue table to stdout. With three regions and totals formatted to two decimals, the output looks like this:

```text
Region: East  Revenue: $2450.00
Region: North  Revenue: $2146.00
Region: South  Revenue: $2031.00
```

Your totals differ because your sample dataset differs. What must match is the shape (one line per region, highest revenue first) and that every region total equals the sum of its records.

---

## Step 2: Identify the Reusable Pattern

**Overview:** Analyze what workflow Claude followed to produce the module. Skills encode decision sequences, not code, so the goal is to name the steps Claude took before any files were written.

**Research / Planning / Discussion:**

```text
Describe the workflow used to build sales-by-region.js as a sequence of named steps. For each step, name:

- What input Claude needed from the user
- What decision Claude made on its own
- What output moved the conversation forward

Do not describe the code. Describe the decision sequence.
```

**Finding:** The response should name discrete steps: clarify input schema, define output contract, implement aggregation, add formatting layer, embed verification sample. If Claude restates what the code does instead of naming the decision steps, redirect: "What did you need to know before you could proceed at each stage?"

**Recipe:**

```text
Describe the workflow we followed to build sales-by-region.js as a numbered sequence of decision steps. For each step state: what information Claude needed before acting, what choice Claude made, and what artifact or decision moved the conversation to the next step.

Do not describe the final code. Describe the process of arriving at it.
```

**Expected Outcome:** A numbered list of 4 to 6 decision steps that reads as a repeatable process, not as a description of the finished code.

---

## Step 3: Create the Skill

**Overview:** Encode the decision sequence from Step 2 into a SKILL.md that Claude can load on demand for similar aggregation tasks. A skill under a project's `.claude/skills/` applies to that project only; copy the folder to `~/.claude/skills/` when you want it available in every project.

**Research / Planning / Discussion:**

```text
Given the decision steps from Step 2, what should the skill's trigger description say? It needs to match phrases a developer would actually type when starting a new aggregation task. Give three candidate trigger sentences and explain the trade-off between being broad (more triggers, less precision) and being narrow (fewer false positives, may miss valid uses).
```

**Finding:** Claude should produce three candidates ranging from narrow ("aggregate sales by region in JavaScript") to broad ("group records by field and sum a numeric column"). The right choice sits in the middle: specific enough to not fire on unrelated requests, general enough to cover more than the single sales scenario. If all three candidates are narrow, ask: "Would this trigger if someone said 'revenue breakdown by product'?"

**Recipe:**

```text
Create a skill at .claude/skills/my-data-aggregator/SKILL.md in this repository. The finished reference already ships as data-aggregator, so the my- prefix keeps both and leaves /data-aggregator working. The skill encodes the workflow we used to build sales-by-region.js.

YAML frontmatter:
- name: my-data-aggregator
- description: one trigger sentence that covers phrases like "aggregate by field", "group sales by region", "revenue breakdown by dimension"

Body sections:

1. Workflow: a numbered list of steps:
   (1) Confirm the input schema: field names, types, which fields are required
   (2) Define the output contract: shape, sort order, key type
   (3) Implement the aggregation function
   (4) Add a formatting function that produces a human-readable single-line-per-group report
   (5) Embed a runnable sample dataset so the module can be verified with node directly

2. Constraints:
   - Use plain JavaScript with no external dependencies
   - Export named functions only
   - Keep business logic in the aggregation function, not the formatter
   - Place the runnable sample at the bottom of the output file, not in a separate test file, wrapped in an if (require.main === module) guard so importing the module prints nothing

Write only SKILL.md. No other files.
```

**Run It:** the description is a guess until something fires it. Trigger the skill by describing a different aggregation task, without naming the skill:

```text
Aggregate orders by product category.
```

**Expected Outcome:** A file `.claude/skills/my-data-aggregator/SKILL.md` with valid YAML frontmatter, a five-step Workflow section, and a Constraints section. Check that the manifest is spelled exactly `SKILL.md`, that `name` matches the folder (`my-data-aggregator`), and that `description` names both what the skill does and the phrases that should trigger it.

The prompt above loads the skill and Claude works through the five steps in order, starting by confirming the input schema rather than writing code. Claude Code watches skill directories and this repository already has `.claude/skills/`, so the new folder is picked up within the session.

