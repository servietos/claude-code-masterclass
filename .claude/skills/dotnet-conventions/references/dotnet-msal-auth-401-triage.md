# MSAL auth: 401 triage and IDX codes

## IDX Error Reference

| Code | Meaning | Fix |
|---|---|---|
| `IDX10214` | Audience validation failed | Make `Audience` match the token's `aud` claim. See the v1/v2 table above. Most common cause: `api://<guid>` config with v2 tokens (bare GUID `aud`). |
| `IDX10205` | Issuer validation failed | Check `TenantId`; v1 tokens come from `https://sts.windows.net/<tid>/`, v2 from `https://login.microsoftonline.com/<tid>/v2.0`. Both should be accepted by `Microsoft.Identity.Web` defaults. |
| `IDX10223` | Token expired | Clock skew or stale token. Check `exp` claim at jwt.ms. |
| `IDX10500` | Signature validation failed | Wrong signing key — usually means token is for a different tenant. |
| `IDX10501` | Signing key not found | Authority/TenantId mismatch — JWKS lookup hit wrong endpoint. |

If `OnAuthenticationFailed` never fires but you still get 401, the request arrived without an `Authorization` header. That is an Angular interceptor problem: check that the `protectedResourceMap` entry uses a `/*` wildcard (MSAL Angular v5 uses strict matching by default).

## 401 Triage Flow

A 401 from the API can come from either the client side (token not attached) or the server side (token rejected). Find which:

1. Open DevTools, Network, select the failed request, check Request Headers for `Authorization: Bearer ...`.
2. If the header is **MISSING**: client problem. Most common cause is the `protectedResourceMap` key missing the `/*` wildcard.
3. If the header is **PRESENT**: server rejected the token. Add the diagnostic block above, restart the API, and retry.

| API console shows | Cause | Next step |
|---|---|---|
| `authHeader=<MISSING>` | Token not attached on the client | Fix MSAL Angular interceptor |
| `OnAuthenticationFailed ... IDX10214` | Audience mismatch | Match `Audience` config to token's `aud` (most likely flip to bare GUID for v2) |
| `OnAuthenticationFailed ... IDX10205` | Issuer mismatch | Verify `TenantId` in config |
| `OnAuthenticationFailed ... IDX10223` | Expired | Re-acquire on the client |
| `OnTokenValidated ...` then 403 | Token valid, scope/role check failed | Check `[RequiredScope]` / policy attributes |
| `OnTokenValidated ...` then 200 | Working — remove diagnostics |  |


Back to the index: [dotnet-msal-auth](dotnet-msal-auth.md)
