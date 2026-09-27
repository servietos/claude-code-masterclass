# Orchestration flow: tasks A to G and the run rules

## Orchestration Flow

Run Tasks A and B in parallel, then C/D/E after the dev server is up, then F/G for analysis. Tasks H and I require explicit user approval before execution.

### Task A: Core Dependencies Upgrade (parallel with B)

1. Read `package.json`: detect Angular version, Material, CDK, NgRx, and other `@angular/*` packages.
2. Run upgrade commands in order:

```bash
ng update @angular/core @angular/cli
ng update @angular/material   # if present
ng update @angular/cdk        # if present
ng update @ngrx/store @ngrx/effects @ngrx/signals  # if present
```

3. Use `--allow-dirty` only if the workspace has uncommitted changes.

### Task B: Dev Environment Setup (parallel with A)

1. Check whether a dev server is already running on port 4200 (or the configured port). Re-use the existing instance; do not kill processes you did not start.
2. If `db.json` exists, run `json-server --watch db.json` in the background.
3. If no server is running and the user has granted permission, run `ng serve` and wait for "Application bundle generation complete".
4. Verify the dev URL is reachable.

### Task C: Runtime Error Audit (after B)

Open the app in the browser via the Chrome DevTools MCP. Capture all console errors and warnings. Categorize: Critical / Warning / Info.

### Task D: Route Testing (after B, parallel with C)

Navigate to key routes. Check for component load errors, signal mismatches, and missing imports.

Task E: Deprecation Analysis (after C and D) has moved to [angular-update-anti-patterns](angular-update-anti-patterns.md).

### Task F: Zoneless Migration Analysis (after E, parallel with G)

- Scan components for `ChangeDetectionStrategy.Default`.
- Count `@Input()` / `@Output()` decorators (non-signal inputs/outputs).
- Check for `NgZone` usage that blocks zoneless migration.
- Generate a migration prerequisites list and effort estimate.

### Task G: Optimization Recommendations (parallel with F)

Identify high / medium / low impact improvements. Present findings as a list before making any code changes.

## Key Rules

- Stop and ask the user if `ng serve` fails — do not attempt workarounds and do not proceed.
- Present full findings before touching any source files.
- Tasks H (codebase refactoring) and I (zoneless migration) require explicit user approval before executing.
- Kill dev servers you started when the session ends; never kill servers you did not start.
- Never run `git` commands or commit without explicit user instruction.

Back to the index: [angular-update](angular-update.md)
