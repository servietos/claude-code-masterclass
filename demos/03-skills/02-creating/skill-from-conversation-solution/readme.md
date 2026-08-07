# Skill from a Proven Conversation (Completed Reference)

The worked-out result of [demo-skill-from-conversation.md](../demo-skill-from-conversation.md). The demo is generative: the learner prompts Claude inside the [skill-from-conversation](../skill-from-conversation/readme.md) starter, which ships empty apart from its readme. Use this folder to compare against what your own conversation produced.

## Contents

| File | Step | What it is |
|---|---|---|
| `sales-by-region.js` | 1 | The dependency-free aggregation module the Step 1 recipe asks for |
| `workflow-steps.md` | 2 | The decision sequence extracted from the Step 1 conversation |
| [`.claude/skills/data-aggregator/SKILL.md`](../../../../.claude/skills/data-aggregator/SKILL.md) | 3 | The skill that encodes the decision sequence, in this repository's harness |

## Run It

```bash
node sales-by-region.js
```

Expected output:

```text
Region: East  Revenue: $2450.00
Region: North  Revenue: $2146.00
Region: South  Revenue: $2031.00
```

## Skill Placement

The finished skill lives in this repository's harness at `.claude/skills/data-aggregator/`, alongside every other skill the course demos use, so invoking `/data-aggregator` from the repository root just works. Only the artifacts a run produces stay in this solution folder.

Your own run writes to `.claude/skills/my-data-aggregator/` in this repository, so both your version and this reference exist side by side. To keep yours, copy that folder into `.claude/skills/` in the project you want it in, or into `~/.claude/skills/` (`$HOME/.claude/skills/` in PowerShell) to make it available in every project.
