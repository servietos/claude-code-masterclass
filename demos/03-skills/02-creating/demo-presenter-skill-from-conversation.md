---
presents: demo-skill-from-conversation.md
budget: 4 min
beats: 4
---

# Present: Create a Skill from a Proven Claude Code Chat

A skill is the decision sequence a conversation proved, not the code that conversation produced. Four beats: the extracted decision steps, the description that is the whole trigger surface, the workflow section, the verification sample.

------

## Beats

### Beat 1: the extractable thing is the decision sequence, not the code (1 min)

**Open:** [`sales-by-region.js`](skill-from-conversation-solution/sales-by-region.js) · [Step 2: Identify the Reusable Pattern](demo-skill-from-conversation.md#step-2-identify-the-reusable-pattern)
**Say:** A conversation ending in working code leaves two things behind, and only one is reusable. The code fits one schema; the order the questions got asked fits the next dataset too.

```text
Describe the workflow we followed to build sales-by-region.js as a numbered sequence of decision steps. For each step state: what information Claude needed before acting, what choice Claude made, and what artifact or decision moved the conversation to the next step.

Do not describe the final code. Describe the process of arriving at it.
```

**Result:** [`workflow-steps.md`](skill-from-conversation-solution/workflow-steps.md), five decision steps; the starter ships a readme and nothing else

```markdown
1. **Confirm the input schema.** Needed from the user: the record shape (`region` string, `product` string, `amount` number) and which fields are required. Decision made alone: treat a missing or non-numeric `amount` as `0` rather than throwing. Artifact that moved the conversation on: an agreed data contract.
...
5. **Embed a runnable verification sample.** Needed: how the learner proves it works. Decision: 8 records across 3 regions at the bottom of the same file so `node sales-by-region.js` is the whole test loop, with no test framework and no dependencies. Artifact: verified stdout.
```

**Gotcha:** when Claude describes the finished code instead, redirect with "What did you need to know before you could proceed at each stage?"

### Beat 2: the description is the entire trigger surface (1 min)

**Open:** [readme.md](readme.md#good-vs-bad-descriptions) · [Step 3: Create the Skill](demo-skill-from-conversation.md#step-3-create-the-skill)
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

### Beat 3: the workflow section is the conversation, compressed (1 min)

**Open:** [`workflow-steps.md`](skill-from-conversation-solution/workflow-steps.md) · the five steps, beside their imperatives
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

**Gotcha:** every explanatory sentence left in the body is paid for on every turn, so the reasoning stays behind in the solution folder.

### Beat 4: verification ships inside the artifact (1 min)

**Open:** [`data-aggregator/SKILL.md`](../../../.claude/skills/data-aggregator/SKILL.md) · the fourth Constraint · [Step 1: Build the Sales Revenue Module](demo-skill-from-conversation.md#step-1-build-the-sales-revenue-module)
**Say:** A skill that generates code is half written until it says how the result gets proven. One command against one file: no framework, no second file, no runner.

```text
At the bottom of the file, add a sample dataset of 8 records spanning 3 regions, then call both functions and log the result inside an if (require.main === module) guard, so the file can be run directly with node sales-by-region.js and stays silent when another module imports it.
```

**Result:** [`sales-by-region.js`](skill-from-conversation-solution/sales-by-region.js) closes on the guard the Constraints require

```javascript
if (require.main === module) {
  const results = salesByRegion(sampleRecords);
  console.log(formatReport(results));
}
```

**Gotcha:** without the guard the report prints on every import; the sample is a verification loop, not a side effect.

## If the room asks

| Question | Answer |
|---|---|
| Why not save the generated file as a template? | A template fixes the field names; the skill fixes the decision order. |
| What does the sample actually print? | Three lines, highest first: `Region: East  Revenue: $2450.00`, `Region: North  Revenue: $2146.00`, `Region: South  Revenue: $2031.00`. |
| Project or home directory? | `.claude/skills/<name>/` covers that project, `~/.claude/skills/<name>/` covers every project; copy the folder, nothing else changes. |
| Claude did not pick the skill up. | If `.claude/skills/` did not exist when the session started it is not being watched yet; restart Claude Code. |
| Should the description name the file it came from? | No. It names what a developer types, and provenance is the classic non-triggering description. |
