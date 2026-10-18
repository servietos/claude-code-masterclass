# Automate a Release CLI with Custom Slash Commands

A custom slash command is a Markdown file that loads only when you invoke it, carrying its own tool pre-approvals and argument substitution. You build three commands against a dependency-free changelog CLI, working through frontmatter fields, positional arguments, and shell injection.

---

Work in `demos/02-harness/03-commands/command-toolkit`, so the project-scoped commands in `.claude/commands/` are discovered; the completed reference is [command-toolkit-solution/](command-toolkit-solution).

## Step 1: Inject Live Command Output with the Bash Prefix

**Overview:** The `` !`command` `` prefix runs a shell command before the file content ever reaches Claude and substitutes the output in place, so the prompt arrives with real data already inlined. Run `node src/notes.mjs 2.4.0` in your terminal first, then build `/notes-for` on that mechanic.

```text
Create .claude/commands/notes-for.md in this project.
Frontmatter:
- description: Render the changelog for a given version and review it for gaps before release
- argument-hint: [version]
- allowed-tools: Read, Bash(node src/notes.mjs *)
Body requirements:
- Show the requested version using `$0`, the placeholder for the FIRST argument.
- Inline the live output of node src/notes.mjs with no argument, using the bash injection prefix on its
  own line.
- Instruct Claude to rewrite the changelog with the requested version in the heading,
  prepend a summary of at most three sentences, and list every entry currently under
  Other Changes together with the grouping key that would fix it.
No inline comments. After creating the file, invoke /notes-for 2.4.0 and show me the result.
```

**Expected Outcome:** The CLI's `## Other Changes` section holds the `sync` and `player` commits, and `/notes-for 2.4.0` replies with a changelog headed `# Release 2.4.0` that calls out both. The injected `node src/notes.mjs` runs with no argument, so the version reaches Claude only through `$0`.

## Step 2: Pass Two Positional Arguments and Change Code with Them

**Overview:** Indexed placeholders split the arguments into distinct values, and their numbering is the single most common trip-up: `$0` is the first argument and `$1` the second, unlike `$1` in a shell script. Build `/add-commit-type` to close the `Other Changes` gap you found in Step 1.

```text
Create .claude/commands/add-commit-type.md in this project.
Frontmatter:
- description: Add a conventional-commit type to the changelog grouping map and cover it with a test
- argument-hint: [type] [heading]
- allowed-tools: Read, Edit, Bash(npm test)
Body: a numbered instruction list that uses the zero-based positional placeholders for
the commit type and the group heading, and tells Claude to
1. Read src/notes.mjs and stop if the type is already a key in GROUPS.
2. Add the type to GROUPS, positioned so the rendered section order still reads as a
   sensible changelog.
3. Add a node:test case to test/notes.test.mjs asserting the new type maps to the new
   heading and is no longer the fallback group.
4. Repoint any existing assertion that used this type as its example of the fallback
   group to a type that is still absent from GROUPS, so the suite stays green.
5. Run npm test and report the pass count.
After creating the file, run /add-commit-type refactor Refactoring.
```

**Expected Outcome:** `src/notes.mjs` gains a `refactor: 'Refactoring'` entry, the existing fallback assertion moves to `build`, and the suite grows from five tests to six, ending in `ℹ pass 6` and `ℹ fail 0`. If Claude says `$1` is the first argument, make it check the documented substitution table before you build on it.

## Step 3: Write a Command That Lints Your Other Commands

**Overview:** A missing `description` makes a command invisible to Claude, and an `argument-hint` that disagrees with the body misleads whoever types it. `/audit-commands` turns those rules into an executable checklist over the `.claude/commands/` folder itself.

```text
Create .claude/commands/audit-commands.md in this project.
Frontmatter:
- description: Lint every slash command file in this project for missing frontmatter fields and argument placeholders
- argument-hint: [strict|report]
- allowed-tools: Read, Glob, Bash(ls .claude/commands)
Body requirements:
- Echo the selected mode using the full-argument-string placeholder, not a positional one.
- Inline the directory listing of .claude/commands using the bash injection prefix.
- Output one table row per command file with columns: command name, missing fields,
  verdict.
After creating the file, run /audit-commands strict.
```

**Expected Outcome:** `/audit-commands strict` returns a table with one row per file, four rows once all four commands are in place, and the injected directory listing at the top matches `ls .claude/commands`.
