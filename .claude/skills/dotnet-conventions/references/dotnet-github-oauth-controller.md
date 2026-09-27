# GitHub OAuth: our controller surface and the token

## Carry the device_code in the request body, NOT a cookie

Do **not** stash the `device_code` in an HttpOnly cookie between `start` and `poll`. Behind a reverse
proxy (Caddy/nginx), cookie `Secure`/`SameSite`/scheme handling makes the cookie go stale or mismatch
across attempts — the classic symptom is polling a code the user never authorized, so it "waits
forever". Instead **return `device_code` from `start` to the SPA and have the SPA send it back on each
`poll`.** The access token is exchanged and stored **server-side** and never reaches the SPA, so this
is safe. It is also deterministic and debuggable.

## Controller shape

- `device/start` → returns `{ deviceCode, userCode, verificationUri, expiresIn, interval }`.
- `device/poll` → `[FromBody]` `{ deviceCode }`; on token, resolve login + persist, return `connected`;
  otherwise return a status (`pending` / `slow_down` (+interval) / `denied` / `expired`).
- `repos` → list `GET /user/repos?per_page=100&sort=updated&affiliation=owner,collaborator,organization_member`;
  include `owner.login` so the UI can distinguish the user's own repos from shared/org repos.
- All endpoints stay behind the app's normal authorization (MSAL/admin) — the SPA attaches its bearer.

## Using the token

Store the token once (single service identity, e.g. a `GitHubAuth` singleton row). Reuse it to clone
private repos by rewriting the URL to `https://x-access-token:<token>@github.com/owner/repo`, and to
list repos. The token is never exposed to the browser.

Back to the index: [dotnet-github-oauth](dotnet-github-oauth.md)
