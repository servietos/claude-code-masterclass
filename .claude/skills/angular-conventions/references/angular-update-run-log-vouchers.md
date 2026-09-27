# Run log: vouchers-ai 21.2.15 to 22.1.2

## Second run: `vouchers-ai` `src/vouchers-ui`, 21.2.15 → 22.1.2 (2026-08-16)

### Second run: `vouchers-ai` `src/vouchers-ui`, 21.2.15 → 22.1.2 (2026-08-16)

Confirms the `CanMatchFn` third-argument break above (one guard spec, fixed with a third `{} as never`). Four things that run did not:

| Item | Detail |
| --- | --- |
| No `.npmrc` means `--force`, not a warning | `ng update` **hard-refuses** when a stable dependency peers on the previous major: `@a2ui/angular@0.10.5` requires `@angular/common ^21.2.5`, so the run aborted with "Incompatible peer dependencies found". With a `legacy-peer-deps=true` `.npmrc` this is a warning; without one it is a wall, and `--force` is the documented way through. Check for the `.npmrc` before predicting which you will get. Later hand-installs still need `--legacy-peer-deps` explicitly |
| A crash on the first `--force` attempt | The forced run died at "Fetching dependency metadata" with Windows exit `3221226505` (`STATUS_STACK_BUFFER_OVERRUN`). Re-running the identical command succeeded and applied every migration. Retry once before investigating |
| View effects now run inside `detectChanges` | Two specs that passed on v21 broke on **test-environment** gaps the effects had never reached: `scrollIntoView is not a function` (jsdom has never implemented it) and a hand-written A2UI double missing `surfaceGroup.getSurface`. Neither is an app bug. Stub the jsdom gap in a setup file (`Element.prototype.scrollIntoView = () => {}`); complete the double for the path that now executes |
| A setup file is inert until registered twice | `src/test-setup.ts` existed but was in neither `angular.json` nor the spec tsconfig. It needs `setupFiles: ["src/test-setup.ts"]` under the `@angular/build:unit-test` target's `options`, **and** an entry in `tsconfig.spec.json` `include` — without the second it still runs but warns "not found in TypeScript compilation" and is not type-checked |

MSAL moved 5 → 6 in the same pass (v6 is the only major supporting Angular 22, see `msal-angular.md`). Where the wiring already matches the v5+ shape — `navigateToLoginRequestUrl` on the `handleRedirectObservable()` call, `logoutRedirect()`, `/*`-suffixed `protectedResourceMap` keys, auth state written into signals — the bump is `npm install --legacy-peer-deps @azure/msal-angular@^6.0.3 @azure/msal-browser@^5.18.0` and **no code change at all**. Verify each of those four before assuming work is needed.

Back to the index: [angular-update](angular-update.md)
