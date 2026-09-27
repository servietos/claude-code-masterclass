# Run log: four workspaces at once, 22.0.1 to 22.1.2, and the e2e aftermath

## Third run: four workspaces in one monorepo, 22.0.1 → 22.1.2 (2026-08-17)

### Third run: four workspaces in one monorepo, 22.0.1 → 22.1.2 (2026-08-17)

A whole portfolio on one framework version, updated as two parallel agents (three admin apps, one
customer portal). Every app was install-only: zero source edits across all four, 776 unit tests green,
and all four images rebuilt. What that run changed in the guidance above:

| Item | Detail |
| --- | --- |
| The hard-refusal is **not** deterministic | The second-run note above says `ng update` hard-refuses without an `.npmrc` when a dependency peers on the previous major. Two of these four apps have no `.npmrc` and `@ngrx/signals` peering `^21.0.0`, and both updated cleanly with no `--force` and no refusal. **Try without `--force` first** and let the tool decide; predicting the wall from the absent `.npmrc` cost nothing here but would have applied `--force` needlessly |
| The Windows crash reproduced a third time | `3221226505` (`STATUS_STACK_BUFFER_OVERRUN`) at "Fetching dependency metadata", identical command succeeded on retry. Three occurrences across three repos: treat one retry as part of the procedure, not as a symptom |
| An unsupported auth SDK drifts silently across a **whole portfolio** | All four apps ran `@azure/msal-angular@^5.x` on Angular 22, which the README matrix says is unsupported (v6 is the only major supporting 22). Nothing surfaced it: `npm outdated` is quiet because 5.x had newer 5.x releases, and the peer range installs fine. When a framework major lands, sweep **every** app's auth SDK support matrix, not just the app you were sent to. All four already had the v5+ call shape, so the fix was `npm install --legacy-peer-deps @azure/msal-angular@^6.0.3 @azure/msal-browser@^5.18.0` and no code change |
| `@ngrx/signals` still has no stable v22 | `{"latest":"21.1.1","next":"22.0.0-rc.0"}`, unchanged from the first run. Rule 2 above holds: stable with an unmet peer, never the RC |
| `CanMatchFn` did not bite | None of the four apps has a `CanMatchFn` guard, so the documented third-argument break never triggered. Grep for it (`grep -rn "CanMatchFn\|canMatch" src/`) rather than assuming the fix is needed |
| `list_projects` under-reports | It gives `frameworkVersion: "22"`, the major only, so it cannot confirm you landed on 22.1.2: read `node_modules/@angular/core/package.json`. It also omitted `unitTestFramework` entirely for these workspaces; read the `test` target's builder out of `angular.json` instead (`@angular/build:unit-test` means Vitest) |
| The generic best-practices guide can contradict a repo hard rule | The v22 guide returned by `get_best_practices` says not to set `changeDetection: ChangeDetectionStrategy.OnPush` explicitly because it is the v22 default, and prefers a new `@Service` decorator over `@Injectable({providedIn: 'root'})`. That repo's agent file mandates explicit OnPush on every component, 88 files' worth. **The repo convention wins and the divergence gets recorded**, so a later session does not "fix" it as an anti-pattern. Report what the guide flagged; do not act on it inside an update task |

## After the upgrade: a red e2e suite is usually not the upgrade

### After the upgrade: a red e2e suite is usually not the upgrade

A 23-failure Playwright suite straight after this upgrade contained **zero** upgrade regressions. The causes were app changes made weeks earlier that no one had re-run the suite against: selectors targeting a `title` attribute that a custom tooltip directive had replaced, specs asserting a server call the app now does client-side, fixtures sitting exactly on a `PAGE_SIZE` boundary, and reads racing an async form load.

Attribute before fixing: `git show HEAD:<file>` at the pre-upgrade commit answers "did this ever work?" in one command. Budget the triage, not the upgrade.

Back to the index: [angular-update](angular-update.md)
