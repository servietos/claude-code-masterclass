# Preflight: prerequisites and the compatibility gate script

## Prerequisites

- Workspace path is known (use `list_projects` to confirm)
- Working branch is clean or has uncommitted changes flagged with `--allow-dirty`
- User has granted explicit approval before any refactoring tasks (Tasks H/I) run

## Version Compatibility Gate (run BEFORE bumping anything)

Run it as a script first, then read the rules below for anything it flags:

```bash
node <this-skill>/scripts/angular-update-preflight.mjs --root src
# per workspace: declared/installed/latest core, TypeScript vs the compiler peer range,
# engines.node vs the running node AND the Dockerfile base tag, the MSAL README matrix,
# and every dependency whose @angular/core peer is unmet, with its dist-tags.
# --workspace <dir> (repeatable), --offline, --json; exits 1 if anything is BLOCKED.
```

It only reports; every decision below stays yours. It exists because each of these checks was a separate
manual command, and skipping one is how the MSAL and Node findings below went unnoticed for a whole
portfolio.

"Update everything to latest" is how a workspace breaks. `npm outdated` reports what is newest, never what is *compatible*. Decide what NOT to bump first, and prove each decision from a file on disk or a registry query rather than from memory. Every rule below was established on a real Angular 22.1.1 / CLI 22.1.3 workspace on 2026-08-10.

Back to the index: [angular-update](angular-update.md)
