---
presents: demo-skill-from-conversation.md
budget: 4 min
beats: 3
---

# Present: Create a Skill from a Proven Claude Code Chat

A skill captures the decision sequence a conversation proved. Three beats: the description that is the whole trigger surface, the workflow section, the verification sample.

------

## Beats

### Beat 1: the description is the entire trigger surface (2 min)

**Open:** [readme.md](readme.md#good-vs-bad-descriptions) · [Step 2: Create the Skill](demo-skill-from-conversation.md#step-2-create-the-skill)
**Say:** Claude reads the description and stops there; it never opens a skill body to decide whether the skill applies. A vague description simply never loads, and nothing errors to tell you.

```text
YAML frontmatter:
- name: my-data-aggregator
- description: one trigger sentence that covers phrases like "aggregate by field", "group sales by region", "revenue breakdown by dimension"
```

**Result:** [`.claude/skills/data-aggregator/SKILL.md`](../../../.claude/skills/data-aggregator/SKILL.md), one capability sentence plus five quoted trigger phrases

```yaml
description: Builds a dependency-free JavaScript module that groups records by a field, sums a numeric column, and prints a one-line-per-group report. Use when the user asks to "aggregate by field", "group sales by region", "revenue breakdown by dimension", "sum orders by product category", or "roll up records into totals".
```

**Gotcha:** the test to say out loud is "Would this trigger if someone said 'revenue breakdown by product'?"; a description that only repeats the original task fails it.

### Beat 2: the workflow section is the conversation, compressed (1 min)

**Open:** [`data-aggregator/SKILL.md`](../../../.claude/skills/data-aggregator/SKILL.md#workflow) · the five steps, beside their imperatives
**Say:** A loaded skill body stays in context for every remaining turn, so length inside it is a recurring cost. Humans need the why to trust a sequence; Claude only needs the imperative.

```text
1. Workflow: a numbered list of steps:
   (1) Confirm the input schema: field names, types, which fields are required
   (2) Define the output contract: shape, sort order, key type
   (3) Implement the aggregation function
   (4) Add a formatting function that produces a human-readable single-line-per-group report
   (5) Embed a runnable sample dataset so the module can be verified with node directly
```

**Result:** the [`data-aggregator`](../../../.claude/skills/data-aggregator/SKILL.md) `## Workflow` section, the same five steps with the reasoning stripped out

```markdown
## Workflow

1. Confirm the input schema: field names, types, and which fields are required.
2. Define the output contract: shape, sort order, and key type.
3. Implement the aggregation function.
4. Add a formatting function that produces a human-readable single-line-per-group report.
5. Embed a runnable sample dataset so the module can be verified with node directly.
```

**Gotcha:** every explanatory sentence left in the body is paid for on every turn, so keep the body to the five imperatives.

### Beat 3: verification ships inside the artifact (1 min)

**Open:** [`data-aggregator/SKILL.md`](../../../.claude/skills/data-aggregator/SKILL.md) · the fourth Constraint · [Step 1: Build the Sales Revenue Module](demo-skill-from-conversation.md#step-1-build-the-sales-revenue-module)
**Say:** A skill that generates code is half written until it says how the result gets proven. One command against one file: no framework, no second file, no runner.

```text
At the bottom of the file, add a sample dataset of 8 records spanning 3 regions, then call both functions and log the result inside an if (require.main === module) guard, so the file can be run directly with node sales-by-region.js and stays silent when another module imports it.
```

**Result:** [`sales-by-region.js`](skill-from-conversation-solution/sales-by-region.js) closes on the guard the Constraints require

```javascript
if (require.main === module) {
  const records = [
    { region: 'East', product: 'Widget', amount: 1200.5 },
    { region: 'North', product: 'Gadget', amount: 1000 },
    { region: 'South', product: 'Gizmo', amount: 990.25 },
    { region: 'East', product: 'Gadget', amount: 850 },
    { region: 'North', product: 'Widget', amount: 646 },
    { region: 'South', product: 'Widget', amount: 1040.75 },
    { region: 'East', product: 'Gizmo', amount: 400 },
    { region: 'North', product: 'Gizmo', amount: 500 },
  ];
  console.log(formatReport(salesByRegion(records)));
}
```

**Gotcha:** without the guard the report prints on every import; the sample is a verification loop with no side effect.

## If the room asks

| Question | Answer |
|---|---|
| Project or home directory? | `.claude/skills/<name>/` covers that project, `~/.claude/skills/<name>/` covers every project; copy the folder, nothing else changes. |
| Claude did not pick the skill up. | If `.claude/skills/` did not exist when the session started it is not being watched yet; restart Claude Code. |
| Should the description name the file it came from? | No. It names what a developer types, and provenance is the classic non-triggering description. |
