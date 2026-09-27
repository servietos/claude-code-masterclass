# Always subscribe to loginRedirect() and logoutRedirect()

**Subscribe to `loginRedirect()` / `logoutRedirect()`, always.** They return Observables. Dropping
them on the floor looks harmless because `msal-angular` wraps a promise chain that fires whether or
not anything subscribes, so a clean session still redirects and the code passes every test. The
failure is the unhappy path: any rejection becomes an unhandled promise rejection with nothing
attached to surface it, so the button visibly does nothing, prints no error a user would find, and
offers no retry. `BrowserAuthError: interaction_in_progress` is the common one, set by MSAL whenever
an earlier redirect did not complete (a closed Microsoft tab, a double click, a stale flag from a
previous session), and it survives in the cache until something clears it. Symptom to recognise:
"the Login button does nothing" on one machine while the same build works on a fresh profile.

Back to the index: [msal-auth-patterns](msal-auth-patterns.md)
