# Create a Skill from a Proven Claude Code Chat

Prompt Claude to build a JavaScript sales-revenue calculator, then extract the decision sequence that conversation proved into a reusable skill. You end with a working `sales-by-region.js` module and a `data-aggregator` SKILL.md whose workflow and constraints replay that same sequence on any new aggregation task.

------

Work in [skill-from-conversation](skill-from-conversation), which ships only a `.claude/settings.json` that keeps the finished `data-aggregator` reference from firing on its own (`/data-aggregator` still works when you type it), so the trigger test in Step 2 can only load your skill; the finished result is in [skill-from-conversation-solution](skill-from-conversation-solution/readme.md).

## Step 1: Build the Sales Revenue Module

Produce a working JavaScript module through prompting. This conversation becomes the raw material for skill extraction: the workflow Claude follows, the decisions it makes, and the structure it produces.

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

**Expected Outcome:** A file `sales-by-region.js` that runs with `node sales-by-region.js` and prints a region-sorted revenue table to stdout:

```text
Region: East  Revenue: $2450.00
Region: North  Revenue: $2146.00
Region: South  Revenue: $2031.00
```

Your totals differ because your sample dataset differs; what must match is the shape (one line per region, highest revenue first) and that every region total equals the sum of its records.

## Step 2: Create the Skill

Encode the decision sequence this conversation proved into a SKILL.md that Claude can load on demand for similar aggregation tasks.

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

The description is a guess until something fires it. Trigger the skill by describing a different aggregation task, without naming the skill:

```text
Aggregate orders by product category.
```

**Expected Outcome:** A file `.claude/skills/my-data-aggregator/SKILL.md` with valid YAML frontmatter, a five-step Workflow section, and a Constraints section.

The prompt loads the skill without naming it, and Claude works through the five steps in order, starting by confirming the input schema.
