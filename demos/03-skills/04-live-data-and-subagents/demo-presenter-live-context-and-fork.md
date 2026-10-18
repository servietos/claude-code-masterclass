---
presents: demo-live-context-and-fork.md
budget: 4 min
beats: 4
---

# Present: Inject Live Project Data and Fork the Audit

A skill can arrive with project data already inside it, and it can hand its work to a second Claude whose reading you never see. Four beats: the data that is already there, the command made to fail, the three lines that move the work elsewhere, the answer citing what was never injected.

------

This topic ships no `-solution` folder. Both finished skills live in the harness, as [`my-order-brief`](../../../.claude/skills/my-order-brief/SKILL.md) and [`my-order-audit`](../../../.claude/skills/my-order-audit/SKILL.md).

## Beats

### Beat 1: the data is in the prompt before Claude has a turn (1 min)

**Open:** [`order-api/src`](order-api/src) · [readme.md](readme.md#dynamic-context-injection)
**Say:** Normally you ask what is in a project and Claude goes and looks, which costs you a turn and lets it pick what to run. Here the commands run first, so the answer is already sitting in the skill by the time Claude reads it.

```text
Body: four sections that inject data with the !`command` syntax, each anchored with ${CLAUDE_PROJECT_DIR} so the commands work no matter which directory Claude Code started in. The project lives at demos/03-skills/04-live-data-and-subagents/order-api.

1. Source files: list the files in the project's src directory
2. Line counts: wc -l over the project's src/*.js
3. Open markers: grep -rn for TODO and FIXME under the project's src
4. Runtime: node --version
```

**Result:** [`.claude/skills/my-order-brief/SKILL.md`](../../../.claude/skills/my-order-brief/SKILL.md). You write placeholders

```markdown
## Source files

!`ls -1 ${CLAUDE_PROJECT_DIR}/demos/03-skills/04-live-data-and-subagents/order-api/src`

## Line counts

!`wc -l ${CLAUDE_PROJECT_DIR}/demos/03-skills/04-live-data-and-subagents/order-api/src/*.js`

## Open markers

!`grep -rn "TODO\|FIXME" ${CLAUDE_PROJECT_DIR}/demos/03-skills/04-live-data-and-subagents/order-api/src`
```

and Claude receives values. This is the same file after substitution, and it is what arrives in the prompt before Claude's first token:

```text
## Source files

index.js
orders.js
pricing.js

## Line counts

  37 .../order-api/src/index.js
  17 .../order-api/src/orders.js
  29 .../order-api/src/pricing.js
  83 total

## Open markers

.../src/orders.js:7:// TODO: reject orders with duplicate SKUs instead of silently summing them
.../src/pricing.js:17:// FIXME: tax is hardcoded to the domestic rate and ignores the shipping country
.../src/pricing.js:22:// TODO: support promotional codes that stack on top of the tier discount
```

**Run:** `/my-order-brief` answers straight from that text: three modules, 83 lines, all three markers by file and line. Show the transcript, because the convincing part is what is absent: no `Bash` call and no permission prompt, recorded in [`order-api/readme.md`](order-api/readme.md)

### Beat 2: prove it is preprocessing by breaking one command (1 min)

**Open:** [readme.md](readme.md#dynamic-context-injection) · [Step 2: Prove It Is Preprocessing](demo-live-context-and-fork.md#step-2-prove-it-is-preprocessing) · `.claude/skills/my-order-brief/SKILL.md` (the learner's own copy, written in Step 1)
**Say:** Treating injection as tool use under another name produces wrong expectations: a retry, a permission gate, a model that could decline. Make one command fail and watch what the session does not do.

```text
Edit .claude/skills/my-order-brief/SKILL.md and add a fifth injected section that runs a command guaranteed to fail, such as listing a directory that does not exist. Invoke /my-order-brief again and tell me what appeared in place of that section, and whether the rest of the brief still worked.
```

**Result:** nothing on disk, by design. On Claude Code 2.1.302 the failing command stops the whole skill: `/my-order-brief` returns no brief, no tool call runs, no permission prompt appears, and the fifth section is removed again inside this step.

### Beat 3: three frontmatter lines move the work somewhere else (1 min)

**Open:** [readme.md](readme.md#running-a-skill-in-a-subagent) · [`my-order-brief/SKILL.md`](../../../.claude/skills/my-order-brief/SKILL.md)
**Say:** A fork is a trade: the skill body becomes another agent's entire prompt, so it works in fresh context and hands back a summary, and it knows nothing about the session that launched it.

```text
Frontmatter:
- name: my-order-audit
- description: names what it does and its trigger phrases
- context: fork
- agent: Explore
- background: false
```

**Result:** [`.claude/skills/my-order-audit/SKILL.md`](../../../.claude/skills/my-order-audit/SKILL.md), three keys apart from the brief and one instruction

```diff
-name: my-order-brief
+name: my-order-audit
+context: fork
+agent: Explore
+background: false
...
-Write the brief from the data above without reading any file.
+Read every file named in the markers above and judge what each marker actually costs in the code around it.
```

### Beat 4: the fork's answer cites what was never injected (1 min)

**Open:** [`order-api/src/orders.js`](order-api/src/orders.js) · [`order-api/src/pricing.js`](order-api/src/pricing.js)
**Say:** Detail in the answer that could not have come from the injected text means files were opened. Those reads landed in a context that is thrown away when the subagent finishes.

```markdown
Read each file named in the markers above and judge what the marker actually costs.

Return a ranked list, highest risk first. One line per marker in the form:

`<file>:<line> | <impact if left unfixed> | <effort: small, medium, large>`
```

**Run:** `/my-order-audit`

**Result:** three ranked lines and nothing else, as the run returned them (paths shortened):

```text
.../order-api/src/pricing.js:17 | wrong totals on every non-domestic order, since tax is always 20% regardless of shipping country | medium (no shipping country on orders; needs a rate table and a signature change through applyPricing)
.../order-api/src/orders.js:7 | silent overbilling when a duplicate line is sent, because subtotalOf sums both copies | small (one validation check in subtotalOf or priceOrder)
.../order-api/src/pricing.js:22 | missing feature only; current totals stay correct, but promo codes cannot be applied | large (new promo model, validation, and stacking rules against the tier discount and tax)

Fix the tax marker in pricing.js:17 first, because it corrupts totals on every order shipped outside the domestic market.
```

Read one name out of that and then scroll back to the injected grep in Beat 1: `applyPricing` and `subtotalOf` appear nowhere in it. The subagent opened the files, in a context you never paid for. Recorded in [`order-api/readme.md`](order-api/readme.md).

## If the room asks

| Question | Answer |
|---|---|
| What if an injected command fails or is slow? | On Claude Code 2.1.302 a failing command stops the whole skill, so no brief comes back; there is no retry, so a slow command is a slow skill. |
| Can a command emit another placeholder? | No. Substitution runs once over the original file and inserted output is not re-scanned. |
| When should the fork stay backgrounded? | For a long audit whose result you do not need this turn; a backgrounded fork also gets the narrower background tool set. |
