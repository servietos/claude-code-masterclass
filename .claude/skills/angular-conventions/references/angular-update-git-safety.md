# ng update and the git index: what it can commit or stage

Upgrade an Angular workspace to the latest version using an orchestrated, parallel flow.

> **⚠️ `ng update` can commit and sweep the working tree. Verify the index yourself; do not assume either way.**
>
> A `maintenance-planner` upgrade saw `ng update` `git commit` its migration changes and stage **everything** dirty in the tree, not just its own edits, bundling unrelated in-flight work into those commits. That violates the repo's "never commit without explicit request" rule, so keep guarding against it.
>
> **What was actually observed on Angular 22.1.3 (2026-08-10) is narrower, and the difference matters.** `ng update` run with `--allow-dirty` on a dirty tree created no commit (`HEAD` stayed at the pre-update sha and `git reflog` gained no entry) and left every change **unstaged**: column 1 of `git status --porcelain` was a space for all 60 paths, checked repeatedly through the session. The tree *did* later turn up fully staged, 60 entries with `M `/`A ` in column 1 and zero unstaged, including files the update never touched (`CLAUDE.md`, `.claude/skills/**`, `.time/working-time.md`, image assets). But `.git/index` was written about ten minutes after the last `ng` command, in a window where no `ng` and no `git` command ran at all, so **the update did not cause it**. In a checkout shared with other sessions or tooling, assume anything can stage your work at any time, and attribute a state change only when you have a timestamp that supports it.
>
> **Procedure:**
> 1. Record a baseline before starting: `git rev-parse HEAD` and `git status --porcelain`, saved somewhere outside the repo.
> 2. After the update, list what is staged with `git status --porcelain | grep -v '^ '` and confirm `git rev-parse HEAD` still matches the baseline sha. Nothing staged and an unchanged HEAD is the clean outcome.
> 3. If the state changed, check `stat -c '%y' .git/index` against the wall-clock time of your last `ng` command before blaming the update. A gap means another writer.
> 4. `--allow-dirty` only lets the update proceed on a dirty tree. It is not a guard against commits or staging, so do not treat passing it as having handled the risk.
> 5. Undoing any of this (`git reset`, `restore`, `checkout`, `stash`, `clean`) is the user's decision, never the agent's. Report the state and stop.

Back to the index: [angular-update](angular-update.md)
