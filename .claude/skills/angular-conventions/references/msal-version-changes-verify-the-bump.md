# Verifying the bump without signing in

### Verifying the bump landed, without signing in

You can prove v5 is really in the bundle without touching auth:

- **Bundle size drops.** v5 hashes error messages to shrink the bundle. The dashboard's initial total went 408.80 kB to 371.03 kB (main 404.94 to 367.17) purely from the major bump.
- **Failures look different at runtime.** Error messages and console logs are hashed, so a v5 failure surfaces as a short code plus a link rather than a sentence. That is expected, not corruption, and it needs the decode script to read.

What a build and a test run **cannot** tell you: anything about the redirect flow. When providers are registered conditionally (`...(environment.authEnabled ? msalProviders : [])`) and the local runtime config ships `authEnabled: false`, MSAL never initializes in dev or in tests. A green suite is silent on auth. The redirect path needs a human clicking through a deployed slot: expect a clean URL with no leftover `#code=`/`?code=` after sign-in, a deep link to survive the round trip, and a reload not to bounce to Microsoft again.

Back to the index: [msal-version-changes](msal-version-changes.md)
