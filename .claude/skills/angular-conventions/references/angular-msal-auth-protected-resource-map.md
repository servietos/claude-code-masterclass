# protectedResourceMap key rules

## `protectedResourceMap` Key Rules

Under MSAL v5 `strictMatching` (the default), the key is a **glob pattern**, not a plain prefix. To cover every path under `/api`, the key MUST end with `/api/*`. The trailing `*` is the whole game.

| Key | Result |
|---|---|
| `https://api.example.com/api/*` | ✅ Correct — attaches token to all `/api/<path>` requests |
| `https://api.example.com/api/` | ❌ No wildcard — strict matching treats this as an exact URL, not a prefix, so real calls like `/api/inventory` get NO token → 401 |
| `https://api.example.com/api` | ❌ Missing trailing slash and wildcard — will not match sub-paths |
| `https://api.example.com` | ❌ Too broad — attaches token to every request including static files |

The `/*` suffix is a special wildcard marker the v5 matcher recognizes. It is not shell glob expansion.

The failure is silent and confusing: the request still goes out (to the correct absolute URL) but with no `Authorization` header, so the API returns 401 and the browser may surface it as a CORS-flavoured error. The server logs show no token-validation failure because no token ever arrived. If you see a 401 with the right URL and no `IDX*` audience/signature error server-side, suspect a missing `*` here first.

Back to the index: [angular-msal-auth](angular-msal-auth.md)
