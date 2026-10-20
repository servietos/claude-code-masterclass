# Test and Package a Skill for Distribution

A skill may never load when someone phrases the request their own way, and once loaded it may quietly skip half of what it promised. You measure both here for this repository's `code-reviewer`, patch what the tests catch, and leave with a folder another team can install.

------

Work in [test-and-package-a-skill](test-and-package-a-skill); the skill itself sits in the harness at [`.claude/skills/code-reviewer/SKILL.md`](../../../.claude/skills/code-reviewer/SKILL.md), and the finished result is in [test-and-package-a-skill-solution](test-and-package-a-skill-solution/dist/README.md).

## Step 1: Measure the Trigger Surface

Trigger behavior comes entirely from the `description` field, and loading is not deterministic, so `trigger-test.sh` (or `trigger-test.ps1`) runs every prompt in `trigger-prompts.tsv` as its own headless session three times. The recorded sweep in [`tests/trigger-cases.md`](test-and-package-a-skill-solution/tests/trigger-cases.md) counts the loads:

```text
| # | Expected | Fires | Observed | Verdict | Prompt |
|---|---|---|---|---|---|
| 1 | fire | 2/3 | fire | pass | Review my changes in ... |
| 2 | fire | 1/2 | unstable | **FAIL** | Can you go through my diff in ... before I push? ... |
```

Then test whether the loaded skill delivers, against a planted defect, because a skill that only says "looks good" passes every test on clean code:

```text
Create a functional test fixture and run it.
1. Add src/discount.ts with a function applyDiscount(price, percent) that divides by percent without
   guarding against zero, reads an API token from a hardcoded string constant, and has no test file.
2. Leave it uncommitted: once committed, git status is clean and both diffs return nothing, so the
   skill's Local Changes workflow has no change left to look at.
3. Invoke the skill by typing row 1 of trigger-prompts.tsv verbatim and leave the skill's name out.
4. Expect the review to miss the file, because a brand-new file shows only as ?? in git status and
   never appears in git diff.
Report which properties failed, including anything the skill could not even gather. Do not fix the
skill yet.
```

Row 1 loaded the skill in none of three runs in this sweep, and the solution's [`review-run-01.md`](test-and-package-a-skill-solution/tests/review-run-01.md) records that the fixture path was already tracked in git HEAD, so `git diff` showed the change.

## Step 2: Patch the Failures the Tests Exposed

Compare a `claude --disallowedTools Skill` session with a plain `claude` session on the planted fixture, and record only the figures you measured. Then fix each failure in the layer that owns it: trigger misses in the `description`, gather gaps in the workflow steps, reporting gaps in the feedback structure.

```text
Edit .claude/skills/code-reviewer/SKILL.md in place to close only the recorded failures.
- Extend the description with the phrasings the sweep showed as missed, and add one clause narrowing
  it away from the no-fire rows that fired. Keep it under the 1024 character frontmatter budget.
- Sharpen the minimum wording in the pillar or feedback section for each missed property.
- Change nothing that no test flagged. Preserve section numbering and heading text.
Then re-run the trigger test and append the new table to trigger-cases.md under a "After the patch"
heading, leaving the first table in place so the delta is readable.
```

**Expected Outcome:** The shipped [`baseline-comparison.md`](test-and-package-a-skill-solution/tests/baseline-comparison.md) reads `not measured` in every cell, and the [solution's `SKILL.md`](test-and-package-a-skill-solution/code-reviewer/SKILL.md) differs in three hunks: the description gains "checking a diff before pushing", section 2 gains `git ls-files --others --exclude-standard`, and section 4 gains a Test Coverage line. Step 3 adds a fourth hunk, the rules-file read in step 1.

Adding trigger keywords to the body changes nothing, because the body is not read until the skill has already loaded.

## Step 3: Give the Skill Your Repo's Facts

A global skill cannot know this repository's folders, prices or test command, so it names a rules file that each repository provides. This step moves those facts into `.claude/rules/code-review.md`, scoped to the source files, and points the skill's first step at that file.

```text
Give the code-reviewer skill this repository's facts without putting any of them in SKILL.md.
1. Create .claude/rules/code-review.md in test-and-package-a-skill with paths: ["src/**/*.ts"] in its frontmatter. Its body states that source lives in src/, that the tests run with npm test, that prices are plain number values in src/cart.ts, and that quote() in src/pricing.ts returns { subtotal, currency } with the currency defaulting to EUR.
2. Edit .claude/skills/code-reviewer/SKILL.md so the first line of step 1 reads: "Read .claude/rules/code-review.md first; if it is missing, review against the general checklist only and say so."
3. Change no other line in SKILL.md, and confirm it names no folder, file or command from this repository.
```

Add the load log to `.claude/settings.json` in the working folder, then run two headless sessions from that folder. The first reads no source file and the second reads `src/pricing.ts`, so the rule should load in the second session only.

```json
{
  "hooks": {
    "InstructionsLoaded": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "cat >> .claude/instructions-loaded.jsonl"
          }
        ]
      }
    ]
  }
}
```

```bash
claude -p "Reply with the single word ready. Do not read any file." < /dev/null
claude -p "Read src/pricing.ts and tell me the return shape of quote()." < /dev/null
```

**Expected Outcome:** `.claude/instructions-loaded.jsonl` holds a `path_glob_match` line for `.claude/rules/code-review.md` with `globs` set to `src/**/*.ts`, written by the second session only. Session-start lines for `CLAUDE.md` files appear in both sessions and are not part of the check.

## Step 4: Package the Skill for Another Team

A skill becomes a product the moment someone else has to install it: a folder plus install documentation for a human who has never seen your repo. Everything the tests produced stays behind, and so does the README, which sits one level up. The repo facts from Step 3 stay behind too, because they live in `.claude/rules/`, outside the skill folder.

```text
Package the code-reviewer skill for external distribution.
1. Create dist/code-reviewer/ holding the patched SKILL.md and nothing else. A skill that had grown
   references/ or scripts/ would carry those too; its tests/ folder still would not.
2. Verify SKILL.md contains no absolute paths and no assumptions about this repository's folder
   names. List every replacement you made.
3. Write dist/README.md for a human installing it: what the skill does in two outcome sentences,
   install steps for Claude Code and for Claude.ai, one worked example prompt, and the measured
   figures from tests/baseline-comparison.md.
4. Zip it so the archive is rooted at code-reviewer/, which means running the command from inside
   dist/, then verify every entry starts with code-reviewer/.
```

**Expected Outcome:** A `dist/code-reviewer/` folder holding `SKILL.md` and nothing test-related, an archive whose every entry starts with `code-reviewer/`, and a [`dist/README.md`](test-and-package-a-skill-solution/dist/README.md) whose opening lines describe what a reviewer gets.

If the two baseline sessions were never captured, the README says so in one line and quotes no figure.
