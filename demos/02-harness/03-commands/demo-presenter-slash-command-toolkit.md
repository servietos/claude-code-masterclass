---
presents: demo-slash-command-toolkit.md
budget: 4 min
beats: 4
---

# Present: Automate a Release CLI with Custom Slash Commands

Four beats: injection before Claude reads the file, zero-based placeholders, `$ARGUMENTS` in a command that lints commands, and the test that breaks when a group is added. A room walks away able to read any command file and say what it grants and what it substitutes.

------

## Beats

### Beat 1: injection runs before Claude sees the file, and it can only carry command output (1 min)

**Open:** [`notes-for.md`](command-toolkit-solution/.claude/commands/notes-for.md) · the `!` injection line and the `$0` above it · [`src/notes.mjs`](command-toolkit-solution/src/notes.mjs)
**Say:** The shell half runs before Claude reads a word, so the turn starts with the output already in it and no instruction to fetch it. It cannot see the arguments you typed.

```markdown
Requested version: $0

Generated changelog:

!`node src/notes.mjs`

Using the changelog above:

1. Rewrite it with `$0` as the version in the `# Release` heading.
```

**Result:** nothing on disk, by design: the rewritten changelog is printed in the reply, and this is the tail the injection inlines from `node src/notes.mjs`

```text
## Other Changes

- **sync**: extract conflict resolution into its own module (@lena.brandt)
- **player**: cover crossfade boundaries with unit tests (@mira.holt)
```

**Gotcha:** `node src/notes.mjs` runs with no argument, so the inlined changelog is always headed `# Release unreleased` and the version arrives only via `$0`.

### Beat 2: positional placeholders are zero-based, unlike a shell script (1 min)

**Open:** [`add-commit-type.md`](command-toolkit-solution/.claude/commands/add-commit-type.md) · the `$0` / `$1` header · [`command-toolkit/src/notes.mjs`](command-toolkit/src/notes.mjs) · the starter's `GROUPS` map
**Say:** Claude Code numbers positional arguments from zero, colliding with the shell habit half the room already has. Nothing errors when the assumption is wrong; the two values simply swap.

```markdown
Commit type: $0
Group heading: $1

1. Read `src/notes.mjs`. If `$0` is already a key in `GROUPS`, stop and report that the type is already mapped.
2. Add `$0: '$1'` to `GROUPS` in `src/notes.mjs`, placed so the rendered section order still reads as a sensible changelog: after the feature, fix and performance entries and before the documentation and chore entries.
```

**Result:** `/add-commit-type refactor Refactoring` put `refactor` in `$0`, and [`command-toolkit-solution/src/notes.mjs`](command-toolkit-solution/src/notes.mjs) gained exactly that pair

```diff
   feat: 'Features',
   fix: 'Bug Fixes',
   perf: 'Performance',
+  refactor: 'Refactoring',
   docs: 'Documentation',
   chore: 'Chores'
 };
```

**Gotcha:** if anyone (or Claude) says `$1` is the first argument, check the substitution table before building anything on it.

### Beat 3: `$ARGUMENTS` and `$N` are different tools, and a command can lint commands (1 min)

**Open:** [`audit-commands.md`](command-toolkit-solution/.claude/commands/audit-commands.md) · the `Mode: $ARGUMENTS` line and the injected `ls` · [Step 3: Write a Command That Lints Your Other Commands](demo-slash-command-toolkit.md#step-3-write-a-command-that-lints-your-other-commands)
**Say:** The shape of the input picks the placeholder: one free-form value wants the whole string, several distinct values want indexes. A folder of command files rots like any other codebase.

```markdown
Mode: $ARGUMENTS

Command directory listing:

!`ls .claude/commands`

...

2. If the frontmatter has an `argument-hint`, the body must use at least one argument placeholder (`$ARGUMENTS`, `$0`, `$1`, ...). Record `argument placeholder` as missing when it does not.
```

**Result:** the listing this command injects into itself, four rows in [`command-toolkit-solution/.claude/commands`](command-toolkit-solution/.claude/commands), three of them written by this demo

```text
add-commit-type.md
audit-commands.md
notes-for.md
release-status.md
```

**Gotcha:** when a room proposes heading-order or line-length rules, ask which of them would change how the command behaves at invocation time.

### Beat 4: adding a group breaks the test that used it as the counter-example (1 min)

**Open:** [`command-toolkit/test/notes.test.mjs`](command-toolkit/test/notes.test.mjs) · the `unknown types fall back to Other Changes` case · [`add-commit-type.md`](command-toolkit-solution/.claude/commands/add-commit-type.md)
**Say:** A suite picks whatever value is currently absent as its example of absence. Make that value present and the assertion that used it has to move to a value that is still absent.

```diff
 assert.equal(groupFor('fix'), 'Bug Fixes');
 });
 
+test('refactor maps to Refactoring', () => {
+  assert.equal(groupFor('refactor'), 'Refactoring');
+  assert.notEqual(groupFor('refactor'), FALLBACK_GROUP);
+});
+
 test('unknown types fall back to Other Changes', () => {
-  assert.equal(groupFor('refactor'), FALLBACK_GROUP);
+  assert.equal(groupFor('build'), FALLBACK_GROUP);
 });
```

**Result:** [`command-toolkit-solution/test/notes.test.mjs`](command-toolkit-solution/test/notes.test.mjs), five tests grow to six, and the suite stays green

```text
ℹ tests 6
ℹ pass 6
ℹ fail 0
```

**Gotcha:** the starter's fallback test used `refactor` as its example of an ungrouped type, so grouping `refactor` turns that green test red.

## If the room asks

| Question | Answer |
|---|---|
| Can I put an injection after `KEY=` on the same line? | No, the `!` is recognised only at line start or after whitespace, so it stays literal text there. |
| What happens to `$2` when I passed two arguments? | It stays in the content unchanged and Claude sees the literal token; escape a genuine `$1` in prose with a backslash. |
