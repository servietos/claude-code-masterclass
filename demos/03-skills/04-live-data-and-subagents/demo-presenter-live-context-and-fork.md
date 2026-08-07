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

  37 demos/03-skills/04-live-data-and-subagents/order-api/src/index.js
  17 demos/03-skills/04-live-data-and-subagents/order-api/src/orders.js
  29 demos/03-skills/04-live-data-and-subagents/order-api/src/pricing.js
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

**Result:** nothing on disk, by design. The failing command's stderr is inlined where its placeholder was, the other four sections are unaffected, no permission prompt appears, and the fifth section is removed again inside this step.

### Beat 3: three frontmatter lines move the work somewhere else (1 min)

**Open:** [readme.md](readme.md#running-a-skill-in-a-subagent) · [`my-order-brief/SKILL.md`](../../../.claude/skills/my-order-brief/SKILL.md)
**Say:** A fork is a trade, not an upgrade. The skill body becomes another agent's entire prompt, so it works in fresh context and hands back a summary, and it knows nothing about the session that launched it.

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
+Read each file named in the markers above and judge what the marker actually costs.
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

**Result:** three ranked lines and nothing else, abridged here at the `...`:

```text
pricing.js:17 | Every order is taxed at 20% regardless of destination; `taxFor` sits on the only
  pricing path (`applyPricing` -> `priceOrder`), so tax and total are silently wrong money on every
  non-domestic order ... | Medium: no order carries a shipping country today, so a country field
  must be threaded through ORDERS -> priceOrder -> applyPricing -> taxFor, touching all three files

orders.js:7 | No monetary error: `subtotalOf` reduces over lines, so two lines of the same SKU sum
  to the same amount ... | Medium: "reject" needs an error path that does not exist, and
  `formatReport` maps over every order, so a throw takes down the whole report

pricing.js:22 | Nothing is wrong today; this is a missing feature ... | Medium: `applyPricing(subtotal)`
  takes a single scalar, so adding codes changes its signature and its one caller
```

Read one name out of that and then scroll back to the injected grep in Beat 1: `taxFor`, `applyPricing`, `subtotalOf`, `formatReport` and the signature `applyPricing(subtotal)` appear nowhere in it. The subagent opened the files, in a context you never paid for. Recorded in [`order-api/readme.md`](order-api/readme.md).

## If the room asks

| Question | Answer |
|---|---|
| What if an injected command fails or is slow? | Its stderr lands in the prompt as text, the rest is unaffected, and there is no retry, so a slow command is a slow skill. |
| Can a command emit another placeholder? | No. Substitution runs once over the original file and inserted output is not re-scanned. |
| When should the fork stay backgrounded? | For a long audit whose result you do not need this turn; a backgrounded fork also gets the narrower background tool set. |
| Can an administrator switch injection off? | Yes, `"disableSkillShellExecution": true` replaces every command with a policy notice, so write skills that fail readably. |
| Is a guidelines skill worth forking? | No. A fork needs a task; a conventions-only skill gives the subagent material and nothing to do. |
