# MSAL Angular - 401 from the API

## 401 Triage — Client Side

A 401 from `https://localhost:5001/api/...` can come from either side. Find which:

1. Open DevTools > Network > failed request > check **Request Headers** for `Authorization: Bearer ...`.
2. If header is **MISSING**, this is a client problem. Most common cause: `protectedResourceMap` key without `/*` wildcard (v5 strict matching). Work through the Troubleshooting table below.
3. If header is **PRESENT**, the server rejected the token. Most common cause: `Audience` config is `api://<guid>` while app issues v2 tokens (token `aud` is bare GUID), causing `IDX10214`. Consult the .NET MSAL reference.

## 401 Troubleshooting

If `https://localhost:5001/api/...` returns 401, work through these in order. (For server-side validation failures, see the .NET MSAL reference.)

### 1. Is the `Authorization` header actually being sent?

Open DevTools > Network > the failing request > Request Headers. If `Authorization: Bearer ...` is **missing**, the interceptor did not match the request URL. Continue to step 2.

If the header is **present**, the problem is server-side — token rejected. Consult the .NET reference's IDX error table.

### 2. `protectedResourceMap` key — strict matching trap

msal-angular v5 enables `strictMatching` by default. Under strict matching, a key without a wildcard suffix only matches that exact URL, not subpaths. The `/*` suffix is a special marker the matcher recognizes as "match this prefix and anything under it".

```typescript
// WRONG — only matches the literal URL "https://localhost:5001/api/" (zero real requests hit this)
protectedResourceMap.set(`${environment.apiUrl}/api/`, scopes);

// CORRECT — matches /api/anything/anything
protectedResourceMap.set(`${environment.apiUrl}/api/*`, scopes);
```

If the interceptor finds no matching key, it silently skips the request and no token is attached, resulting in 401 with `Authorization` header absent.

**Counter-intuitive note:** the `/*` is NOT shell glob expansion — it is parsed by the matcher. The literal `*` character is the documented v5 wildcard form.

### 3. Is the user signed in?

In DevTools > Application > Local Storage, look for keys like `msal.<clientId>.account.keys` and `msal.<clientId>-login.<tenant>-accesstoken-...`. If absent, the login redirect never completed; verify `redirectUri` matches the SPA registration in Azure AD.

### 4. Is the interceptor in the HttpClient chain?

`provideHttpClient(withInterceptorsFromDi(), withFetch())` — the `withInterceptorsFromDi()` is **required** because `MsalInterceptor` is registered via the class-based `HTTP_INTERCEPTORS` token. Without it, the interceptor is silently dropped.

### 5. Did the first HTTP call fire before MSAL settled?

If a store or component fires an HTTP request from its constructor or `APP_INITIALIZER`-adjacent code, it may run before `inProgress$` reaches `InteractionStatus.None` and the active account is set. Symptom: first request 401s, subsequent requests succeed.

Fix: gate HTTP calls behind `msalBroadcastService.inProgress$.pipe(filter(s => s === InteractionStatus.None))` or behind a "ready" signal in `AuthStateService`.

Back to the index: [msal-troubleshooting](msal-troubleshooting.md)
