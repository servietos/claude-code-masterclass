# The /api/about Build-Identity Endpoint

## `/api/about`: exposing build identity alongside health

A health probe answers "is it up". An about endpoint answers "*which build* is up", which is what a
fleet or ops dashboard actually needs. Keep both, anonymous, and give them one shape across every API
in a portfolio so a single client can consume all of them:

```json
{
  "slot": "blue", "imageTag": "ghcr.io/org/app:blue", "container": "86944018cf85",
  "environment": "Production", "runtime": ".NET 10.0.10", "version": "a1b2c3d",
  "gitTag": "main", "gitSha": "a1b2c3d4e5f6",
  "startedAtUtc": "2026-07-31T17:56:02Z", "uptimeSeconds": 323,
  "status": "healthy", "checks": { "database": "healthy" }
}
```

Values flow `docker build --build-arg` -> `ARG` -> `ENV Deployment__*` -> config binding -> DTO.

### The `"unknown"` sentinel trap

The Dockerfile `ARG`s default to the literal string `"unknown"`. If the CI workflow never passes
`build-args:`, the endpoint returns **HTTP 200 with every build field reading `"unknown"`**. The
feature looks shipped, the probe looks green, and the data is worthless. This survives review easily
because nothing errors.

- **Verify the values, never just the status code.** `curl` the deployed endpoint and read the payload.
  A 200 is not evidence the wiring works.
- **Never render the sentinel.** A client must treat `""`, whitespace, and `"unknown"` as absent
  (one shared `isUnknown()` helper) and omit the element or show a neutral placeholder. Printing the
  word "unknown" to a customer is worse than printing nothing.
- Where no workflow computes a real git tag, `GIT_TAG` honestly degrades to the branch name. Say so
  rather than inventing a tagging scheme; `gitSha` is the real build identity.

Back to the index: [dotnet-health-checks](dotnet-health-checks.md)
