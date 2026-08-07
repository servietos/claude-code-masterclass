---
presents: demo-slash-command-toolkit.md
budget: 6 min
beats: 6
---

# Present: Automate a Release CLI with Custom Slash Commands

One seed command file taken apart, three more built on top of it, ending in an audit of the whole folder. A room walks away able to read any command file and say what it grants and what it substitutes.

------

## Beats

### Beat 1: the filename is the command, and `allowed-tools` is a pre-approval (1 min)

**Open:** [`release-status.md`](command-toolkit/.claude/commands/release-status.md) · the frontmatter, lines 1 to 5 · [`src/notes.mjs`](command-toolkit/src/notes.mjs)
**Say:** A handful of frontmatter keys are everything configurable about a command. `allowed-tools` reads like a restriction but is a one-turn pre-approval.

```yaml
---
description: Summarize the commit fixture and report which commit types the changelog CLI does not group yet
argument-hint: [version]
allowed-tools: Read, Glob, Bash(node src/notes.mjs *)
---
```

**Result:** the starter ships this one file; the run wrote three more on the same three keys, such as [`add-commit-type.md`](command-toolkit-solution/.claude/commands/add-commit-type.md)

```yaml
description: Add a conventional-commit type to the changelog grouping map and cover it with a test
argument-hint: [type] [heading]
allowed-tools: Read, Edit, Bash(npm test)
```

**Gotcha:** the file name without the extension is the command name, so this file is `/release-status`; nothing inside the file declares it.

### Beat 2: injection runs before Claude sees the file, and it carries data, not arguments (1 min)

**Open:** [`notes-for.md`](command-toolkit-solution/.claude/commands/notes-for.md) · the `!` injection line and the `$0` above it · [`src/notes.mjs`](command-toolkit-solution/src/notes.mjs)
**Say:** The shell half runs before Claude reads a word, so the turn starts from data instead of an instruction to fetch it. It cannot see the arguments you typed.

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

### Beat 3: positional placeholders are zero-based, unlike a shell script (1 min)

**Open:** [`add-commit-type.md`](command-toolkit-solution/.claude/commands/add-commit-type.md) · the `$0` / `$1` header · [`command-toolkit/src/notes.mjs`](command-toolkit/src/notes.mjs) · the starter's `GROUPS` map
**Say:** Claude Code numbers positional arguments from zero, colliding with the shell habit half the room already has. Nothing errors when the assumption is wrong; the two values simply swap.

```markdown
Commit type: `$0`
Group heading: `$1`

Do the following in order:

1. Read `src/notes.mjs` and confirm `$0` is not already a key in `GROUPS`. If it is, stop and say so.
2. Add `$0: '$1'` to the `GROUPS` map, placed so the rendered section order stays sensible for a changelog.
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

### Beat 4: `$ARGUMENTS` and `$N` are different tools, and a command can lint commands (1 min)

**Open:** [`audit-commands.md`](command-toolkit-solution/.claude/commands/audit-commands.md) · the `Mode: $ARGUMENTS` line and the injected `ls` · [Step 5: Write a Command That Lints Your Other Commands](demo-slash-command-toolkit.md#step-5-write-a-command-that-lints-your-other-commands)
**Say:** The shape of the input picks the placeholder: one free-form value wants the whole string, several distinct values want indexes. A folder of command files rots like any other codebase.

```markdown
Mode: $ARGUMENTS

Command files on disk:

!`ls .claude/commands`

...

- `argument-hint` is present and its bracket count matches the highest positional placeholder used in the body.
- `allowed-tools` is present and lists only tools the body actually needs.
```

**Result:** the listing this command injects into itself, four rows in [`command-toolkit-solution/.claude/commands`](command-toolkit-solution/.claude/commands), three of them written by this demo

```text
add-commit-type.md
audit-commands.md
notes-for.md
release-status.md
```

**Gotcha:** when a room proposes heading-order or line-length rules, ask which of them would change how the command behaves at invocation time.

### Beat 5: adding a group breaks the test that used it as the counter-example (1 min)

**Open:** [`command-toolkit/test/notes.test.mjs`](command-toolkit/test/notes.test.mjs) · the `unknown types fall back to Other Changes` case · [`add-commit-type.md`](command-toolkit-solution/.claude/commands/add-commit-type.md)
**Say:** A suite picks whatever value is currently absent as its example of absence. Make that value present and it is the assertion that is wrong, not the code.

```diff
 test('unknown types fall back to Other Changes', () => {
-  assert.equal(groupFor('refactor'), FALLBACK_GROUP);
+  assert.equal(groupFor('build'), FALLBACK_GROUP);
+});
+
+test('refactor is grouped under Refactoring', () => {
+  assert.equal(groupFor('refactor'), 'Refactoring');
+  assert.notEqual(groupFor('refactor'), FALLBACK_GROUP);
 });
```

**Result:** [`command-toolkit-solution/test/notes.test.mjs`](command-toolkit-solution/test/notes.test.mjs), five tests to six rather than five to five plus a failure

```text
✔ unknown types fall back to Other Changes (0.0671ms)
✔ refactor is grouped under Refactoring (0.4414ms)
...
ℹ pass 6
ℹ fail 0
```

**Gotcha:** the starter's fallback test used `refactor` as its example of an ungrouped type, so grouping `refactor` turns that green test red.

### Beat 6: scope is a property of the command, not of where you happened to save it (1 min)

**Open:** [`command-toolkit/readme.md`](command-toolkit/readme.md) · it ends at `## What you add` · `~/.claude/commands/audit-commands.md` (personal scope, outside this repo)
**Say:** The project folder ships with the repository, the home folder follows the person. What settles the placement is whether the body names anything that exists only here.

```text
Write a short migration note at the bottom of the starter's readme.md, at most eight lines,
that records:

- Which of the four commands stay in this project's .claude/commands/ and why.
- Which one is a candidate for personal scope so it applies across projects, and the exact
  path it would move to.
- What would have to change about the file if it were promoted from a single .md file into
  a skill folder instead.
```

**Result:** a Command Scope Migration Note in [`command-toolkit-solution/readme.md`](command-toolkit-solution/readme.md), a section the starter has no counterpart for

```markdown
`/audit-commands` is the cross-project candidate: it lints command files against rules that hold in any repository. Its personal-scope destination is `~/.claude/commands/audit-commands.md`.
```

**Gotcha:** precedence runs enterprise over personal over project, and a command file and a same-named skill folder both produce `/name`, with the skill winning the collision.

## If the room asks

| Question | Answer |
|---|---|
| Does `allowed-tools` stop Claude calling anything else? | No, it pre-approves the listed shapes for one turn; unlisted tools stay callable under your normal permission settings. |
| Can I put an injection after `KEY=` on the same line? | No, the `!` is recognised only at line start or after whitespace, so it stays literal text there. |
| What happens to `$2` when I passed two arguments? | It stays in the content unchanged and Claude sees the literal token; escape a genuine `$1` in prose with a backslash. |
