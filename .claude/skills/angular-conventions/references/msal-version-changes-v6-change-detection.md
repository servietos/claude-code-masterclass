# The v6 change-detection caveat

### The v6 change-detection caveat, and why signals satisfy it

v6 auto-initializes the client inside `loginRedirect`, `acquireTokenSilent`, `ssoSilent` and friends, which removes most `uninitialized_public_client_application` errors. In exchange, **components subscribing to `inProgress$` or `msalSubject$` must trigger change detection themselves** after mutating state, via `cdr.detectChanges()` / `markForCheck()`.

A service that writes subscription results into **signals** already satisfies this: signal writes notify consumers on their own, and the upgrade guide names signals as the recommended alternative to manual CD. No change needed for the `AuthStateService` pattern below. A component that assigns to a plain field in a `subscribe()` callback does need the fix.

Still required in v6, unchanged: subscribe to `handleRedirectObservable()` once at startup, and gate interactive calls on `inProgress$ === InteractionStatus.None`.

Back to the index: [msal-version-changes](msal-version-changes.md)
