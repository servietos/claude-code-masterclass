# Trigger Cases

Description under test, quoted verbatim from `.claude/skills/code-reviewer/SKILL.md` before the patch:

```text
Use this skill to review code. It supports both local changes (staged or working tree) and remote Pull Requests (by ID or URL). It focuses on correctness, maintainability, and adherence to project standards.
```

Every row below is a real headless session started inside this project, prompted with no mention of the skill. A run counts as `fire` when its transcript contains a tool call named `Skill`.

| # | Expected | Fires | Observed | Verdict | Prompt |
|---|---|---|---|---|---|
| 1 | fire | 2/3 | fire | pass | Review my changes in demos/03-skills/05-test-and-package/test-and-package-a-skill. |
| 2 | fire | 1/2 | unstable | **FAIL** | Can you go through my diff in demos/03-skills/05-test-and-package/test-and-package-a-skill before I push? I do not want to break anything. |
| 3 | fire | 1/1 | fire | pass | Anything risky in what I just added under demos/03-skills/05-test-and-package/test-and-package-a-skill? |
| 4 | no-fire | 0/1 | no-fire | pass | Write a helper in demos/03-skills/05-test-and-package/test-and-package-a-skill that formats currency for the quote output. |
| 5 | no-fire | 0/1 | no-fire | pass | Refactor quote in demos/03-skills/05-test-and-package/test-and-package-a-skill to take an options object instead of a currency argument. |
| 6 | no-fire | 0/1 | no-fire | pass | Explain how the cart total is calculated in demos/03-skills/05-test-and-package/test-and-package-a-skill. |

Row 1 is the interesting one and it is not a failure. Three identical sessions, two loads: the skill fires on the phrasing its description was written for, and still not every time. Loading is a model decision rather than a lookup, so a trigger row is a rate, and a table of booleans would have hidden that.

Row 2 is the miss the patch closes. Two runs under different harness settings disagreed, and no configuration has yet repeated it three times, so it is recorded as unstable rather than as a clean no-fire. The description offers "staged or working tree" while the developer writes "diff" and "push", which shares no word with it.

## What was not measured

Rows 3 to 6 were run once each rather than three times. They agree with the prediction, and a single agreeing run is weak evidence: treat them as unconfirmed rather than as results worth quoting. Re-running the sweep settles them.

The sweep costs one session per run, roughly a minute each, and it edits nothing only because it runs in plan mode. An earlier configuration that denied the editing tools by name still let rows 4 and 5 write files into `src/`, which is why the script pins the permission mode instead.
