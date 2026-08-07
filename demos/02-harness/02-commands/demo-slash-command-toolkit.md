# Automate a Release CLI with Custom Slash Commands

A custom slash command is a Markdown file that loads only when you invoke it, carrying its own tool pre-approvals and argument substitution. You take one seed command apart, then build three more against a dependency-free changelog CLI, working through frontmatter fields, positional arguments, shell injection, and project versus personal scope. You finish with a four-command toolkit and the ability to audit any command file you are handed.

---

## Setup

Open a Claude Code session with the starter folder as the working directory, so the project-scoped commands in `.claude/commands/` are discovered:

```bash
cd demos/02-harness/02-commands/command-toolkit
npm install
npm test
```

The project has zero dependencies, so `npm install` completes offline in under a second. All five starter tests must pass before you begin.

---

## Step 1: Read the Seed Command and Name Its Parts

**Overview:** The starter ships exactly one command file, `.claude/commands/release-status.md`. Before writing new ones, take it apart and establish where the command name comes from and what each frontmatter key buys you.

**Research / Planning / Discussion:**

```text
Read .claude/commands/release-status.md in this project.

Answer these, one or two sentences each:
1. What determines the name I type to invoke this command?
2. What does each frontmatter key in this file do, and which of them are optional?
3. What does the $ARGUMENTS token in the body expand to, and what happens if I invoke the command with arguments but the body has no $ARGUMENTS?
4. What exactly does the allowed-tools value grant for Bash in this command, and how long does that grant last?

Do not create or edit any files.
```

**Finding:** A good answer states that the file name without the extension becomes the command name, so `release-status.md` yields `/release-status`. It should identify `description` as what Claude uses to decide relevance, `argument-hint` as autocomplete-only text, and `allowed-tools` as a pre-approval that clears when you send your next message rather than a restriction on what Claude may call. On the fourth question it should note that `Bash(node src/notes.mjs *)` pre-approves only that one command shape. If Claude claims `allowed-tools` blocks unlisted tools, push back: unlisted tools remain callable and simply fall back to your normal permission settings.

**Recipe:**

```text
Read .claude/commands/release-status.md and produce a two-column table mapping every
frontmatter key and every template token in the body to a one-sentence explanation of
its effect at invocation time.

Then add one closing paragraph answering: if I renamed the file to
.claude/commands/release/status.md, what would change about how I invoke it, and is
that behaviour something you can confirm from the Claude Code documentation or only
guess at? Say plainly which it is.

Do not modify any files.
```

**Expected Outcome:** A table with rows for `description`, `argument-hint`, `allowed-tools` and `$ARGUMENTS`, and a closing paragraph that distinguishes documented behaviour from assumption. This step's response is model-generated, so the exact wording varies between runs; what must appear is the file-name-to-command-name rule and the turn-scoped nature of `allowed-tools`.

---

## Step 2: Run the CLI and the Seed Command Against Real Output

**Overview:** A command is only worth writing if the underlying tool is worth running. Run the changelog CLI yourself, then invoke `/release-status` and compare what it reports against what you just saw on stdout.

**Research / Planning / Discussion:**

First run the CLI directly in your terminal:

```bash
node src/notes.mjs 2.4.0
```

Then, in the Claude Code session:

```text
/release-status 2.4.0
```

**Finding:** The CLI prints a grouped markdown changelog and ends with a commit count. Compare its `## Other Changes` section against the `GROUPS` map in `src/notes.mjs`: two commit types in the fixture have no group and fall through. `/release-status` should name those same two types. If its table disagrees with the terminal output, it read the fixture carelessly, so ask it to re-count from `data/commits.json` rather than from memory.

**Recipe:**

```text
Run node src/notes.mjs 2.4.0 and read src/notes.mjs.

Report:
- The commit types present in data/commits.json with a count for each.
- Which of those types are absent from the GROUPS map.
- The exact heading each ungrouped commit currently renders under.

Then recommend, in one sentence, which single missing type is most worth adding first
and why.
```

**Expected Outcome:** The terminal shows the grouped changelog. The tail of the real output from the starter is:

```text
## Chores

- **deps**: bump the audio decoder to 4.2.0 (@dev.okoye)
- **ci**: cache the node modules directory between runs (@mira.holt)

## Other Changes

- **sync**: extract conflict resolution into its own module (@lena.brandt)
- **player**: cover crossfade boundaries with unit tests (@mira.holt)

_14 commits in this release._
```

Claude's `/release-status` reply must independently identify `refactor` and `test` as the two ungrouped types.

---

## Step 3: Inject Live Command Output with the Bash Prefix

**Overview:** So far Claude has had to run the CLI itself. The `` !`command` `` prefix runs a shell command before the file content ever reaches Claude and substitutes the output in place, so the prompt arrives with real data already inlined. Build `/notes-for` on that mechanic.

**Research / Planning / Discussion:**

```text
In a Claude Code command file, a line can contain !`some command`.

Explain, in short paragraphs:
1. When does that command run relative to Claude seeing the file content?
2. What replaces the placeholder, and is the substituted output itself scanned for more
   placeholders?
3. Where must the ! character appear on the line for the form to be recognised?
4. What is the multi-line equivalent of the inline form?
5. Which frontmatter key must cooperate so the injection does not trigger a permission
   prompt every time?

Answer only from the Claude Code documentation on skills and custom commands. If you
cannot confirm one of these, say so instead of guessing.
```

**Finding:** Claude should say the command runs before Claude sees anything, that its stdout replaces the placeholder as plain text and is not re-scanned, and that the `!` is only recognised at the start of a line or immediately after whitespace. It should name the fenced block opened with three backticks followed by `!` as the multi-line form, and connect the injection to a matching `allowed-tools` Bash pattern. A strong answer also mentions that the `disableSkillShellExecution` setting can switch the whole mechanism off. If it claims `KEY=` followed by an injection works, push back: with `!` following a non-whitespace character the placeholder stays literal text.

**Recipe:**

```text
Create .claude/commands/notes-for.md in this project.

Frontmatter:
- description: Render the changelog for a given version and review it for gaps before release
- argument-hint: [version]
- allowed-tools: Read, Bash(node src/notes.mjs *)
- model: claude-sonnet-5

Body requirements:
- Show the requested version using the positional placeholder for the FIRST argument.
- Inline the live output of node src/notes.mjs using the bash injection prefix on its
  own line.
- Instruct Claude to rewrite the changelog with the requested version in the heading,
  prepend a summary of at most three sentences, and list every entry currently under
  Other Changes together with the grouping key that would fix it.
- End by stating the result is printed in the reply and no files are written.

No inline comments. After creating the file, invoke /notes-for 2.4.0 and show me the result.
```

**Expected Outcome:** `.claude/commands/notes-for.md` exists and `/notes-for 2.4.0` appears in the command menu with the hint `[version]`. The reply contains a rewritten changelog headed `# Release 2.4.0` plus a summary paragraph. The prose is model-generated and differs run to run; the fixed signals are the version heading and the call-out of the two `Other Changes` entries.

Note what the injection does and does not carry. `node src/notes.mjs` runs with no argument, so the inlined changelog is always headed `# Release unreleased`; the requested version reaches Claude only through the `$0` placeholder in the body, which is why the body has to instruct the rewrite of the heading. The injection gives you the commit data for free, not the version.

---

## Step 4: Pass Two Positional Arguments and Change Code with Them

**Overview:** `$ARGUMENTS` gives you the whole argument string, which is useless when a command takes two distinct values. Indexed placeholders solve that, and their numbering is the single most common trip-up. Build `/add-commit-type` to close the `Other Changes` gap you found in Step 2.

**Research / Planning / Discussion:**

```text
Compare the argument placeholders available in a Claude Code command file:
$ARGUMENTS, $ARGUMENTS[N], $N, and named arguments declared in frontmatter.

Answer precisely:
1. If I invoke /example alpha beta, what does $0 expand to? What about $1?
2. How do I pass a two-word value as a single argument?
3. What happens to $2 if only two arguments were supplied?
4. How do I write a literal $1 in prose without it being substituted?

State the indexing base explicitly and say whether it matches shell positional
parameters.
```

**Finding:** The critical signal is that indexing is zero-based: `$0` is the first argument and `$1` the second, unlike `$1` in a shell script. Claude should also say that indexed arguments use shell-style quoting so `"hello world"` arrives as one value, that an indexed placeholder with no matching argument is left in the content unchanged, and that a backslash escapes the token. If Claude says `$1` is the first argument, stop and make it check the documented substitution table before you build anything on top of it.

**Recipe:**

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

State that no inline comments are written and nothing beyond those edits changes.

After creating the file, run /add-commit-type refactor Refactoring.
```

**Expected Outcome:** `src/notes.mjs` gains a `refactor: 'Refactoring'` entry, the existing fallback assertion moves to a type that is still ungrouped (`build`), `test/notes.test.mjs` gains a case for `refactor`, and the suite grows from five tests to six. A real run in the solution folder prints, with the timings varying per run:

```text
✔ known types map to their group heading (0.4189ms)
✔ unknown types fall back to Other Changes (0.0671ms)
✔ refactor is grouped under Refactoring (0.4414ms)
✔ groupCommits buckets every commit (3.9142ms)
✔ renderChangelog emits the version heading and a commit count (1.0819ms)
✔ every configured group has a non-empty heading (0.1206ms)
ℹ tests 6
ℹ suites 0
ℹ pass 6
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 64.7744
```

Re-running `node src/notes.mjs 2.4.0` now shows a `## Refactoring` section, and `## Other Changes` holds a single entry.

---

## Step 5: Write a Command That Lints Your Other Commands

**Overview:** A toolkit of commands rots the same way code does: a missing `description` makes a command invisible to Claude, and an `argument-hint` that disagrees with the body misleads whoever types it. `/audit-commands` turns the rules you learned in Steps 1 to 4 into an executable checklist over the `.claude/commands/` folder itself.

**Research / Planning / Discussion:**

```text
Look at every file in .claude/commands/ in this project.

Propose a lint rule set for command files, five rules at most, where each rule is
mechanically checkable by reading the file. For each rule state:
- The rule in one sentence.
- The concrete failure it prevents.
- Whether it should be a hard failure or a warning.

Pay particular attention to rules that catch a command Claude will never choose to use,
and to allowed-tools entries that are broader than the body needs.

Do not write the command file yet.
```

**Finding:** Expect a missing-or-vague `description` rule to be ranked as a hard failure, since without it Claude has no basis for deciding relevance. Look for a rule tying the bracket count in `argument-hint` to the highest positional placeholder in the body, and a rule flagging a bare `Bash` in `allowed-tools` where a scoped `Bash(pattern *)` would do. If the proposed rules are stylistic (heading order, line length) rather than behavioural, push back and ask which of them would actually change how the command behaves at invocation time.

**Recipe:**

```text
Create .claude/commands/audit-commands.md in this project.

Frontmatter:
- description: Lint every slash command file in this project for missing frontmatter fields and argument placeholders
- argument-hint: [strict|report]
- allowed-tools: Read, Glob, Bash(ls .claude/commands)

Body requirements:
- Echo the selected mode using the full-argument-string placeholder, not a positional one.
- Inline the directory listing of .claude/commands using the bash injection prefix.
- Check every .md file in .claude/commands/ against these rules: frontmatter present and
  first in the file; description present and descriptive; argument-hint present with a
  bracket count matching the highest positional placeholder used; allowed-tools present
  and no broader than the body needs; body references at least one argument placeholder.
- Output one table row per command file with columns: command name, missing fields,
  verdict.
- In strict mode fail any command granting a bare Bash with no argument pattern; in
  report mode record it as a warning.
- Forbid modifying any command file; fixes are proposed in prose only.

After creating the file, run /audit-commands strict.
```

**Expected Outcome:** `.claude/commands/audit-commands.md` exists, and `/audit-commands strict` returns a table with one row per file, four rows once all four commands are in place. The verdicts are Claude's judgement and vary between sessions; the observable signal is that every file in `.claude/commands/` appears exactly once in the table and that the injected directory listing at the top matches `ls .claude/commands`.

---

## Step 6: Decide Where Each Command Lives

**Overview:** All four commands currently sit in the project's `.claude/commands/`, which means they travel with the repository to every teammate. Two of them are project-specific and one is not, and the docs also describe a folder-based form that a single file eventually outgrows. Make that call deliberately rather than by default.

**Research / Planning / Discussion:**

```text
Using the Claude Code documentation on skills and custom commands, explain:

1. The difference in reach between a command stored in this project's .claude/ folder and
   one stored under your home .claude/ folder.
2. The documented relationship between a file in .claude/commands/ and a skill folder
   containing SKILL.md, including which wins when both share a name.
3. What a skill folder can do that a single command file cannot.
4. Which precedence applies when the same name exists at enterprise, personal and project
   level.

Then classify /release-status, /notes-for, /add-commit-type and /audit-commands: which
belong to this repository, and which is generic enough to follow you across projects?
Justify each in one sentence.
```

**Finding:** Claude should state that a project-level file ships with the repo and applies only there, while a personal-level one applies to all your projects, and that precedence runs enterprise over personal over project. On the second question it must say the two forms create the same `/name` and behave the same way, with the skill winning a name collision, and that a skill folder adds supporting files, templates and scripts. On the classification, `/audit-commands` is the outlier: it lints command files, a task that is identical in every repository, so it is the natural candidate for personal scope. If Claude proposes moving `/add-commit-type` out of the project, push back: it edits `src/notes.mjs` by name and is meaningless elsewhere.

**Recipe:**

```text
Write a short migration note at the bottom of the starter's readme.md, at most eight lines,
that records:

- Which of the four commands stay in this project's .claude/commands/ and why.
- Which one is a candidate for personal scope so it applies across projects, and the exact
  path it would move to.
- What would have to change about the file if it were promoted from a single .md file into
  a skill folder instead.

Keep it factual, no em dashes, and change nothing else in the file.
```

**Expected Outcome:** The starter's `readme.md` gains a short migration note naming `/audit-commands` as the cross-project candidate and giving a concrete destination path under your home `.claude/` folder. The reasoning is model-generated and will not match word for word between runs.


---

The completed reference, with all four command files, the extended `GROUPS` map and the sixth test in place, is [command-toolkit-solution/](command-toolkit-solution/).
