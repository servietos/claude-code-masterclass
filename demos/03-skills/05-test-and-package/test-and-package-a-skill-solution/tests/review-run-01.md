# Review Run 01 (fixture run, pre-patch skill)

Fixture run: one headless session with the prompt from Step 1 of the demo guide, started in this folder with `--permission-mode bypassPermissions` on `claude-haiku-5-5`. Session `98f4d891-d213-4abf-b167-9808aed602b8`.

The session wrote `src/discount.ts` itself, because the working copy did not exist before the run. Its path is tracked in git HEAD from an earlier commit of this folder, so `git status` reports ` M` for it, not `??`, and `git diff` shows the change. The premise that a brand-new file is invisible to both diffs does not hold for this path.

The session did not invoke the `code-reviewer` skill, so zero `Skill` calls appear in its transcript. It gathered with `git status` and `cat`, and wrote its own findings.

Planted defects, as the session reported them:

- Unguarded division: flagged, `percent = 0` gives `Infinity` and the function returns `0` for `applyDiscount(100, 0)`.
- Hardcoded token: flagged on line 1.
- Missing test file: not mentioned in any finding.

The session's own conclusion: "The fixture did not produce the condition the test depends on, so the run is not a valid test of the "miss the new file" property."
