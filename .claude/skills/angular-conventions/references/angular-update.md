# Angular App Update

Upgrade an Angular workspace to the latest version using an orchestrated, parallel flow.

> **⚠️ `ng update` auto-commits — and sweeps the whole working tree.** Run inside a git repo, `ng update` automatically `git commit`s its migration changes, and it stages **everything** dirty in the tree — not just its own edits — bundling unrelated in-flight work (and files outside `src/ui`) into those commits. This violates the repo's "never commit without explicit request" rule. **Mitigations:** commit or stash unrelated work first so the tree is clean before updating; OR run and then immediately undo the auto-commits with a mixed reset to the pre-update HEAD (`git reset <baseline-sha>`), which restores every change as uncommitted working-tree edits (verify byte-content afterward). Do NOT use `--allow-dirty` as a substitute for this awareness — it lets the update proceed on a dirty tree but does nothing to stop the auto-commit sweep.

## Prerequisites

- Workspace path is known (use `list_projects` to confirm)
- Working branch is clean or has uncommitted changes flagged with `--allow-dirty`
- User has granted explicit approval before any refactoring tasks (Tasks H/I) run

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

### Task E: Deprecation Analysis (after C and D)

Cross-reference console warnings with the Angular breaking-changes log. Categorize by severity using the registry below.

**Anti-pattern registry:**

| Anti-pattern | Severity |
|---|---|
| `@Input()` / `@Output()` decorators instead of `input()` / `output()` | Critical |
| `*ngIf` / `*ngFor` / `*ngSwitch` instead of `@if` / `@for` / `@switch` | Critical |
| `standalone: true` explicitly set (redundant in v20+) | High |
| `async pipe + Observable` for HTTP reads instead of `httpResource()` | High |
| `toSignal(http.get(...))` instead of `httpResource()` | High |
| `subscribe()` in component body | High |
| `BehaviorSubject` for local state instead of `signal()` | Medium |
| Constructor injection instead of `inject()` | Medium |
| `ChangeDetectionStrategy.Default` on components | Medium |
| `@HostBinding` / `@HostListener` instead of `host` object | Medium |
| `ngClass` / `ngStyle` instead of `[class.x]` / `[style.x]` bindings | Medium |
| Reactive Forms / `ngModel` where Signal Forms apply | Medium |

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

## Angular 22 Upgrade (Completed)

`maintenance-planner` `src/ui` was upgraded **21.2.9 → 22.0.5** (all `@angular/*` plus `cli`/`build`/`devkit` packages) via `ng update @angular/core@22 @angular/cli@22`. Non-obvious steps from that run, for the next upgrade:

| Item | Detail |
| --- | --- |
| TypeScript peer bump | Angular 22 requires **TypeScript 6.0.3** (was 5.9.3) — the schematic applied it automatically |
| NgRx stays pinned | `@ngrx/signals` / `@ngrx/operators` remained at **21.1.0** (no v22 build exists yet); the existing `legacy-peer-deps=true` in `.npmrc` absorbed the peer warning with **no `--force` needed**. Do not bump NgRx to a non-existent v22 |
| Automated migration: HTTP testing | `withXhr` added to `provideHttpClient()` in HTTP-testing specs — Angular 22 defaults `HttpClient` to the **Fetch** backend, and `HttpTestingController` needs XHR |
| Automated migration: templates | `$safeNavigationMigration()` wrapper added to templates (stricter optional-chaining/null-propagation); tsconfig `extendedDiagnostics` suppressions added for `nullishCoalescingNotNullable` / `optionalChainNotNullable` |
| Manual fix the schematic missed | Angular 22's `CanMatchFn` gained a required **third `currentSnapshot: PartialMatchRouteSnapshot` argument**. The automated migration does not rewrite direct test invocations of guards — guard `.spec.ts` files calling `canMatchAuth(route, segments)` / `reservationCanMatch(...)` broke compilation; fixed by adding a third `null as any` argument at each test call site. The guard implementations themselves compile fine with fewer params |
| Signal Forms | No API delta in 22 — still `@experimental` (see `angular-forms.md`) |
