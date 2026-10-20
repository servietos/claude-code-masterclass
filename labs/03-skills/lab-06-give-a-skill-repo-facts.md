# Give a Skill Your Repo's Facts Through a Rules File

A review skill that carries one repo's source folder, money rules and release process in its own body works in that repo and nowhere else. This lab moves those facts into `.claude/rules/`, where the skill reads the file it names, and adds an `InstructionsLoaded` hook that records each time Claude Code loads a rules file. You finish with one skill that reviews against whichever area of the repo you name.

What you practice here: a repo-agnostic skill that reads a named rules file, a path-scoped rule next to an unscoped rule, and a hook log that shows when each one loads. The rule mechanics are explained in the [constitution topic](../../demos/02-harness/02-constitution/readme.md); this lab applies them.

Duration: about 20 minutes.

------

The starter is the pristine copy, so you work in a copy outside the repo. The skill sits in `.claude/skills/` of the folder Claude Code starts in, which is why the copy is the folder you open. A global skill in `~/.claude/skills/` follows the same rules.

Copy the starter from the repo root. Bash:

```bash
cp -r labs/03-skills/repo-facts-skill "$HOME/repo-facts-lab"
```

PowerShell:

```powershell
Copy-Item -Recurse labs\03-skills\repo-facts-skill "$HOME\repo-facts-lab"
```

Then open the copy in a terminal. Every command below runs from this folder.

```bash
cd "$HOME/repo-facts-lab"
```

```powershell
Set-Location "$HOME\repo-facts-lab"
```

Each `claude -p` command below answers once and exits, and the hook you register in step 4 records what it loaded. You can paste the same prompts into an interactive `claude` session instead.

---

## Step 1: Open the Skill and Run It Without Rules

**Overview:** Read the skill before you change anything. Its first step names a rules file, and this run shows what the skill does while that file is missing.

**Recipe:** Open `.claude/skills/area-reviewer/SKILL.md` in your editor and find step 1. Then run:

```text
claude -p "Use the area-reviewer skill for area code-review to review src/pricing.ts. Report the rules file you read, or say that it is missing." --strict-mcp-config --disallowedTools Edit Write NotebookEdit Bash PowerShell
```

**Expected Outcome:** The answer says that `.claude/rules/code-review.md` is missing, then reviews `src/pricing.ts` against the general checklist only and says so. The general checklist can still catch the fractional result in `applyDiscount`. The answer does not cite a money rule from the repo, because none is loaded yet. The skill carries no repo facts of its own.

---

## Step 2: Write the Rules File With a paths: Scope

**Overview:** Facts about one part of the code go into a rules file with `paths:`. Claude Code loads that file only when it reads a file that matches the glob, so these facts apply to `src/**/*.ts` and nowhere else.

**Recipe:** Create `.claude/rules/code-review.md` with this content:

```markdown
---
paths:
  - "src/**/*.ts"
---

# Code review facts

- Application source lives in `src/`. Review TypeScript files there against these facts.
- Money is an integer number of cents. A function that returns an amount returns whole cents.
- Round once, at the last step of a calculation, and name the rounding rule you apply.
```

Then run the same command as step 1 again.

**Expected Outcome:** The answer cites the integer cents rule and flags the return line of `applyDiscount` in `src/pricing.ts`, because that result can hold a fraction of a cent. The wording varies from run to run. The flagged line stays the same.

---

## Step 3: Write the Second Rule Without paths:

**Overview:** Facts that span the whole repo, such as the release process, get no `paths:` line. Claude Code loads a rule without `paths:` at launch, in every session.

**Recipe:** Create `.claude/rules/release.md` with this content. It has no frontmatter.

```markdown
# Release facts

- Every change under `src/` gets one line under `## Unreleased` in `CHANGELOG.md`.
- The version lives in `package.json`. A release bumps it in the same commit as the changelog entry.
```

**Expected Outcome:** `.claude/rules/` holds two files. Only `code-review.md` has a `paths:` line. Step 5 shows when each file loads.

---

## Step 4: Register an InstructionsLoaded Hook

**Overview:** The hook runs each time Claude Code loads an instruction file and appends one JSON line to `instructions-log.txt`. It cannot block a load, so it only records what happened.

**Recipe:** Create `.claude/settings.json` with this content:

```json
{
  "hooks": {
    "InstructionsLoaded": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "node .claude/hooks/log-instructions.mjs"
          }
        ]
      }
    ]
  }
}
```

Create `.claude/hooks/log-instructions.mjs` with this content:

```js
import { appendFileSync } from 'node:fs';
import { join } from 'node:path';

const chunks = [];
for await (const chunk of process.stdin) chunks.push(chunk);
const input = JSON.parse(Buffer.concat(chunks).toString('utf8'));

const entry = {
  at: new Date().toISOString(),
  load_reason: input.load_reason,
  file_path: input.file_path,
  globs: input.globs ?? null,
  trigger_file_path: input.trigger_file_path ?? null,
};

appendFileSync(join(input.cwd, 'instructions-log.txt'), JSON.stringify(entry) + '\n');
```

Check that the script parses:

```bash
node --check .claude/hooks/log-instructions.mjs
```

```powershell
node --check .claude\hooks\log-instructions.mjs
```

**Expected Outcome:** The check prints nothing. The settings file has no `matcher`, so the hook logs every load reason. A matcher such as `"session_start"` would narrow the hook to one reason.

---

## Step 5: Watch When Each Rule Loads

**Overview:** Two sessions show the two timings. The first reads only the rules file, so the path-scoped rule must stay out of the log. The second reads `src/pricing.ts`, which matches the glob, so the path-scoped rule loads then.

**Recipe:** Run the first session, then print the log:

```text
claude -p "Use the area-reviewer skill for area code-review. Read only the rules file and list its bullet points. Do not open any file under src/." --strict-mcp-config --disallowedTools Edit Write NotebookEdit Bash PowerShell
```

```bash
cat instructions-log.txt
```

**Expected Outcome:** The log has a `session_start` line for `.claude/rules/release.md` with `"globs":null`. It has no line for `code-review.md`, although the answer quotes its bullets: the skill read that file itself, and a read of a non-matching file loads nothing. Your user-level `CLAUDE.md` adds a `session_start` line too; ignore any line whose path is not under `.claude/rules/`.

**Recipe:** Run the second session, then print the log again:

```text
claude -p "Use the area-reviewer skill for area code-review to review src/pricing.ts. Report each finding on one line." --strict-mcp-config --disallowedTools Edit Write NotebookEdit Bash PowerShell
```

```bash
cat instructions-log.txt
```

**Expected Outcome:** A new line comes after the lines the first session wrote. It has `"load_reason":"path_glob_match"`, a `file_path` ending in `.claude/rules/code-review.md`, `"globs":["src/**/*.ts"]` and a `trigger_file_path` ending in `src/pricing.ts`. The answer cites the cents rule. The skill reads the rules file in its own step 1, so the facts do not depend on the path rule loading, and that explicit read is why the skill names its file.

---

## Step 6: Point the Same Skill at the Second Rules File

**Overview:** The area named in the request decides which rules file the skill reads. Nothing in `SKILL.md` changes, and the file under review stays `src/pricing.ts`.

**Recipe:**

```text
claude -p "Use the area-reviewer skill for area release to review src/pricing.ts. Apply only the rules of area release and report each finding on one line." --strict-mcp-config --disallowedTools Edit Write NotebookEdit Bash PowerShell
```

**Expected Outcome:** The finding now cites the release rule: the copy has no `CHANGELOG.md`, so no `## Unreleased` entry covers `src/pricing.ts`. The cents finding from the step 5 review is gone, because the request says to apply only the rules of the named area. The path rule still loads, since `src/pricing.ts` matches its glob, so the log gains a second `path_glob_match` line for `code-review.md`.

---

## Verify

Run this from the working copy. Bash:

```bash
find .claude -type f
```

PowerShell:

```powershell
Get-ChildItem -Recurse -File .claude
```

**Expected Outcome:** Five files: `skills/area-reviewer/SKILL.md`, `rules/code-review.md`, `rules/release.md`, `settings.json` and `hooks/log-instructions.mjs`. `instructions-log.txt` holds one JSON line per load from all three runs. Open `labs/03-skills/repo-facts-skill-solution/` to compare your copy file by file.

To finish, delete the working copy folder. The starter in the repo has not changed.
