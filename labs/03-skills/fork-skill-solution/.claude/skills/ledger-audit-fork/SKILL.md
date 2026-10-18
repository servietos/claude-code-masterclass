---
name: ledger-audit-fork
description: Audit the open TODO and FIXME markers in the ledger-service project in an isolated subagent and return only the ranking. Use when the user asks for a forked ledger audit, a quiet risk ranking, or an audit that must not fill the main session.
context: fork
agent: Explore
background: false
---

# ledger-audit-fork

## Open markers

!`grep -rn "TODO\|FIXME" ${CLAUDE_PROJECT_DIR}/src`

## Line counts

!`wc -l ${CLAUDE_PROJECT_DIR}/src/*.js`

## Task

Read every file named in the markers above and judge what each marker costs by reading the code around it. Treat the comment's wording as a hint at most.

Return a list ranked by risk, highest first, one line per marker:

<file>:<line> | <impact if left unfixed> | <effort>

Close with one sentence naming what to fix first. Return nothing else: no preamble, no file summaries, no restatement of the markers.
