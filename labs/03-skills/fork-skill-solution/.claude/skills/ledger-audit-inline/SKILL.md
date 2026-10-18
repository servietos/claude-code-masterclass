---
name: ledger-audit-inline
description: Audit the open TODO and FIXME markers in the ledger-service project and rank them by risk. Use when the user asks for a ledger audit, a risk ranking of the open markers, or which marker to fix first.
---

# ledger-audit-inline

## Open markers

!`grep -rn "TODO\|FIXME" ${CLAUDE_PROJECT_DIR}/src`

## Line counts

!`wc -l ${CLAUDE_PROJECT_DIR}/src/*.js`

## Task

Read every file named in the markers above and judge what each marker costs by reading the code around it. Treat the comment's wording as a hint at most.

Return a list ranked by risk, highest first, one line per marker:

<file>:<line> | <impact if left unfixed> | <effort>

Close with one sentence naming what to fix first. Return nothing else: no preamble, no file summaries, no restatement of the markers.
