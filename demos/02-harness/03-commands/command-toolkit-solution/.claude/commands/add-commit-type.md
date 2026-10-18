---
description: Add a conventional-commit type to the changelog grouping map and cover it with a test
argument-hint: [type] [heading]
allowed-tools: Read, Edit, Bash(npm test)
---

# Add Commit Type

Commit type: $0
Group heading: $1

1. Read `src/notes.mjs`. If `$0` is already a key in `GROUPS`, stop and report that the type is already mapped.
2. Add `$0: '$1'` to `GROUPS` in `src/notes.mjs`, placed so the rendered section order still reads as a sensible changelog: after the feature, fix and performance entries and before the documentation and chore entries.
3. Add a `node:test` case to `test/notes.test.mjs` that asserts `groupFor('$0')` equals `'$1'` and does not equal `FALLBACK_GROUP`.
4. Find any existing assertion that uses `$0` as its example of the fallback group, and repoint it to a type that is still absent from `GROUPS` and differs from `$0` (for example `build` or `style`), so the suite stays green.
5. Run `npm test` and report the pass count.
