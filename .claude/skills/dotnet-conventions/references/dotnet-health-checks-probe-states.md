# Cross-Origin Probe States

### Consuming it cross-origin: probe states are not HTTP statuses

A browser dashboard on a different origin cannot map HTTP status to UI state naively:

- The endpoint must list the dashboard origin in `Cors:AllowedOrigins`. Keep that in the checked-in
  `appsettings.json` so the fix ships **inside the image**, with no hand-managed box env change.
- A redirecting hostname (`www` -> apex) is useless as an allowed origin: a redirect never carries the
  preflight. Allow the canonical host.
- **A 404 without CORS headers is indistinguishable from a network failure**, so a client cannot tell
  "endpoint absent" from "host unreachable". Design the state machine for that, not against it.

Map outcomes to intent, and pick tone by *who reported the fault*:

| Outcome | State | Tone |
| --- | --- | --- |
| 200, `status`/`checks` all healthy | `ok` | success |
| 200 or 503 with any `unhealthy` value | `degraded` | **danger** (the service reported a real fault) |
| 404 | `absent` | neutral |
| network error, CORS failure, timeout | `unreachable` | **neutral, never danger** |

The rule: **red means the service told us something is wrong; muted means we could not ask it.**
A slot running an older image, or one merely blocked by CORS, is usually serving production traffic
perfectly. Painting it red says "this app is down" and is simply false.

Back to the index: [dotnet-health-checks](dotnet-health-checks.md)
