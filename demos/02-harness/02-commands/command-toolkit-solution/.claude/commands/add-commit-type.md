---
description: Add a conventional-commit type to the changelog grouping map and cover it with a test
argument-hint: [type] [heading]
allowed-tools: Read, Edit, Bash(npm test)
---

# Add Commit Type

Commit type: `$0`
Group heading: `$1`

Do the following in order:

1. Read `src/notes.mjs` and confirm `$0` is not already a key in `GROUPS`. If it is, stop and say so.
2. Add `$0: '$1'` to the `GROUPS` map, placed so the rendered section order stays sensible for a changelog.
3. Add a `node:test` case to `test/notes.test.mjs` asserting that `groupFor('$0')` returns `'$1'` and that it is no longer the fallback group.
4. Run `npm test` and report the pass count.

Write no inline comments. Change nothing else.
