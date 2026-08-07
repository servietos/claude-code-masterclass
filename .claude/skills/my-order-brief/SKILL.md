---
name: my-order-brief
description: Brief the order-api demo project's source layout, size, and open maintenance markers. Use when the user asks for a project brief of order-api, what is in the order-api codebase, how big it is, or where its open TODOs and FIXMEs are.
---

# my-order-brief

## Source files

!`ls -1 ${CLAUDE_PROJECT_DIR}/demos/03-skills/04-live-data-and-subagents/order-api/src`

## Line counts

!`wc -l ${CLAUDE_PROJECT_DIR}/demos/03-skills/04-live-data-and-subagents/order-api/src/*.js`

## Open markers

!`grep -rn "TODO\|FIXME" ${CLAUDE_PROJECT_DIR}/demos/03-skills/04-live-data-and-subagents/order-api/src`

## Runtime

!`node --version`

## Config

!`ls -1 ${CLAUDE_PROJECT_DIR}/demos/03-skills/04-live-data-and-subagents/order-api/config`

## Instructions

Write the brief from the data above without reading any file.

1. One sentence naming the module count and total lines.
2. One line per open marker: file, line number, and what it asks for.
3. One sentence naming which file carries the most risk and why.

Stay under 12 lines. If a section above is empty, say so rather than inferring its contents.
