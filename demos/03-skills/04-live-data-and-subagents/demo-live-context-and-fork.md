# Inject Live Project Data and Fork the Audit

A skill can arrive with real project data already inside it, so Claude answers without going to look first. It can also hand its work to a second Claude, whose reading you never have to see.

------

Open Claude Code at the repository root; the project under audit is [order-api](order-api), and the finished skills already sit in the harness as [`my-order-brief`](../../../.claude/skills/my-order-brief/SKILL.md) and [`my-order-audit`](../../../.claude/skills/my-order-audit/SKILL.md).

## Step 1: Inline the Evidence

Write a skill whose prompt already contains the project's file listing, line counts, and open markers, so Claude answers without a single tool call.

```text
Create a skill at .claude/skills/my-order-brief/SKILL.md in this repository.

Frontmatter:
- name: my-order-brief
- description: names what it does and the phrases that should trigger it

Body: four sections that inject data with the !`command` syntax, each anchored with ${CLAUDE_PROJECT_DIR} so the commands work no matter which directory Claude Code started in. The project lives at demos/03-skills/04-live-data-and-subagents/order-api.

1. Source files: list the files in the project's src directory
2. Line counts: wc -l over the project's src/*.js
3. Open markers: grep -rn for TODO and FIXME under the project's src
4. Runtime: node --version

Then an Instructions section telling Claude to write the brief from the data above without reading any file: module count and total lines, one line per marker with file and line number, and one sentence naming the riskiest file. Cap it at 12 lines.

Write only SKILL.md.
```

**Expected Outcome:** Invoking `/my-order-brief` returns a brief naming all three markers by file and line: `orders.js:7`, `pricing.js:17`, and `pricing.js:22`, plus the 83-line total and your Node version. The verified reference output is in [order-api/readme.md](order-api/readme.md).

Claude answers without opening a file, because the four sections arrive in the prompt already filled in.

## Step 2: Prove It Is Preprocessing

Confirm that the commands ran before Claude saw the prompt. This is the mechanic learners most often misread.

```text
Edit .claude/skills/my-order-brief/SKILL.md and add a fifth injected section that runs a command guaranteed to fail, such as listing a directory that does not exist. Invoke /my-order-brief again and tell me what appeared in place of that section, and whether the rest of the brief still worked.
```

**Expected Outcome:** On Claude Code 2.1.302 the failing command stops the whole skill: `/my-order-brief` returns no brief, and the other four sections do not render either. Nothing prompts you for permission, because no tool was called. Remove the failing section before moving on.

No `Bash` call appears in the transcript, so injection is preprocessing: no retry, no permission gate, and no model that could decline.

## Step 3: Fork the Same Evidence into a Subagent

Take the same injected evidence, hand it to an Explore subagent with `context: fork`, and compare what returns to your main context.

```text
Create a skill at .claude/skills/my-order-audit/SKILL.md in this repository.

Frontmatter:
- name: my-order-audit
- description: names what it does and its trigger phrases
- context: fork
- agent: Explore
- background: false

Body: inject the same TODO and FIXME grep and the same wc -l line counts, anchored with ${CLAUDE_PROJECT_DIR}. Then a task section telling the subagent to read each file named in the markers and judge what the marker costs, returning a list ranked by risk, one line per marker as <file>:<line> | <impact if left unfixed> | <effort>, closing with one sentence naming what to fix first and nothing else.

Write only SKILL.md.
```

**Expected Outcome:** `/my-order-audit` returns a ranked list and nothing else, with `pricing.js:17` first, because a hardcoded tax rate produces wrong money on orders the system already accepts. Run `/context` after each skill: the inline brief keeps its injected output in your session; the audit keeps only its summary.

The ranking cites details that appear nowhere in the injected text, such as the `applyPricing` and `subtotalOf` function names, which proves the subagent opened the files in its own context.
