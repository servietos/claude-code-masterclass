# MSAL Angular — Version Choice and Breaking Changes

Which `@azure/msal-angular` major to run against which Angular, and exactly what changed at each hop.
Read before an upgrade and when an API that used to exist no longer compiles.

**On Angular 22, only msal-angular v6 is supported**, and v6 requires `@azure/msal-browser ^5.18.0`, so the two move together.

| You want to... | Read |
| --- | --- |
| Know which major your Angular version supports (`npm outdated` cannot tell you) | [msal-version-changes-support-matrix](msal-version-changes-support-matrix.md) |
| Fix an MSAL API that no longer compiles: the v4 to v5 removals and moves | [msal-version-changes-v5-api-breaks](msal-version-changes-v5-api-breaks.md) |
| Perform the v4 to v6 upgrade, and make the one code change it forces | [msal-version-changes-v4-to-v6-upgrade](msal-version-changes-v4-to-v6-upgrade.md) |
| Run the pre-bump greps over `src/`, and see what survives untouched | [msal-version-changes-removed-api-audit](msal-version-changes-removed-api-audit.md) |
| Find out whether `inProgress$` / `msalSubject$` now need `cdr.detectChanges()` | [msal-version-changes-v6-change-detection](msal-version-changes-v6-change-detection.md) |
| Decide whether your app needs the v5 redirect-bridge page | [msal-version-changes-redirect-bridge](msal-version-changes-redirect-bridge.md) |
| Prove v5 is really in the bundle without signing in | [msal-version-changes-verify-the-bump](msal-version-changes-verify-the-bump.md) |
