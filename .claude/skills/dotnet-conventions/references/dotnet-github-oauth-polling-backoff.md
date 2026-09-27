# GitHub OAuth: poll errors, slow_down and the gotchas checklist

## The `slow_down` back-off is mandatory (the #1 bug)

Map GitHub's poll errors and **honor `slow_down`**:

| GitHub `error` | Client action |
|---|---|
| `authorization_pending` | Keep polling, do not exceed `interval` |
| `slow_down` | **Increase the interval by 5s** and keep polling (RFC 8628 §3.5) |
| `access_denied` | Stop — user declined |
| `expired_token` | Stop — request a new device code |

If you ignore `slow_down` and keep polling at the original rate, GitHub returns `slow_down` on **every**
subsequent request and **never processes the authorization** — the UI hangs on "waiting" even though
the user authorized. Return the interval to the client so it can back off; poll at `interval + 1s`
initially to avoid tripping it at all.

```csharp
public sealed record PollResult(string? Token, string? Pending, int Interval);
// ... on non-token response: return new PollResult(null, body?.Error, body?.Interval);
```

## Gotchas checklist

- OAuth App must have **Enable Device Flow** ticked, or `start` returns `device_flow_disabled`.
- No `client_secret` anywhere — device flow does not use one.
- `Accept: application/json` on both GitHub calls.
- Honor `slow_down` (+5s) — otherwise infinite "waiting".
- `device_code` travels in the request body, not a cookie.
- Client ID lives in `appsettings.json` (public), not `.env`.

Back to the index: [dotnet-github-oauth](dotnet-github-oauth.md)
