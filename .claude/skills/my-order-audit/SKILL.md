---
name: my-order-audit
description: Audit the open maintenance markers in the order-api demo project and rank them by risk. Use when the user asks for a code audit of order-api, a risk ranking of its TODOs and FIXMEs, which order-api marker to fix first, or what the open markers there actually cost.
context: fork
agent: Explore
background: false
---

# my-order-audit

## Open markers

!`grep -rn "TODO\|FIXME" ${CLAUDE_PROJECT_DIR}/demos/03-skills/04-live-data-and-subagents/order-api/src`

## Line counts

!`wc -l ${CLAUDE_PROJECT_DIR}/demos/03-skills/04-live-data-and-subagents/order-api/src/*.js`

## Task

The project is at `${CLAUDE_PROJECT_DIR}/demos/03-skills/04-live-data-and-subagents/order-api`.

Read every file named in the markers above and judge what each marker actually costs in the code around it, not from the wording of the comment.

Return a list ranked by risk, highest first, one line per marker:

```text
<file>:<line> | <impact if left unfixed> | <effort>
```

Close with one sentence naming what to fix first.

Return nothing else: no preamble, no file summaries, no restatement of the markers.
