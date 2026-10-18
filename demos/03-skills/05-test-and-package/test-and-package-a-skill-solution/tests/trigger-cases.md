# Trigger Cases

Description under test, quoted verbatim from `.claude/skills/code-reviewer/SKILL.md` (the installed copy, unpatched):

```text
Use this skill to review code. It supports both local changes (staged or working tree) and remote Pull Requests (by ID or URL). It focuses on correctness, maintainability, and adherence to project standards.
```

Every row below is a real headless session started inside this project with `trigger-test.sh`, prompted with no mention of the skill, three sessions per row on `claude-haiku-5-5`. A run counts as `fire` when its transcript contains a tool call named `Skill`.

| # | Expected | Fires | Observed | Verdict | Prompt |
|---|---|---|---|---|---|
| 1 | fire | 0/3 | no-fire | **FAIL** | Review my changes in demos/03-skills/05-test-and-package/test-and-package-a-skill. |
| 2 | fire | 0/3 | no-fire | **FAIL** | Can you go through my diff in demos/03-skills/05-test-and-package/test-and-package-a-skill before I push? I do not want to break anything. |
| 3 | fire | 0/3 | no-fire | **FAIL** | Anything risky in what I just added under demos/03-skills/05-test-and-package/test-and-package-a-skill? |
| 4 | no-fire | 0/3 | no-fire | pass | Write a helper in demos/03-skills/05-test-and-package/test-and-package-a-skill that formats currency for the quote output. |
| 5 | no-fire | 0/3 | no-fire | pass | Refactor quote in demos/03-skills/05-test-and-package/test-and-package-a-skill to take an options object instead of a currency argument. |
| 6 | no-fire | 0/3 | no-fire | pass | Explain how the cart total is calculated in demos/03-skills/05-test-and-package/test-and-package-a-skill. |

Rows 1 to 3 are the prompts the description was written for, and none of the three sessions loaded the skill. The default-model sweep that ran first (`claude-sonnet-5-5`) also returned 0/3 on rows 1 to 3, so the miss does not depend on the model. Rows 4 to 6 agree with the prediction, and three agreeing runs each is still a small sample.

In a diagnostic session, row 1 under `--permission-mode bypassPermissions` also made no `Skill` call and answered with two `Bash` calls that inspected the folder, so the miss is not caused by plan mode.

## Not measured

The re-run after the patch needs the patched `SKILL.md` installed at `.claude/skills/code-reviewer/SKILL.md`, which sits outside this unit, so no "After the patch" table exists yet.
