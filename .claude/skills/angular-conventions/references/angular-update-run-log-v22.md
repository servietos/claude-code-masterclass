# Run log: maintenance-planner 21.2.9 to 22.0.5

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

Back to the index: [angular-update](angular-update.md)
