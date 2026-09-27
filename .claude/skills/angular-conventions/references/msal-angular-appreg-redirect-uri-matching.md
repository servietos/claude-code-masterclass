# SPA vs Web platform and AADSTS50011

## Platform Types: SPA vs Web

| Platform | Use for | Auth flow |
|---|---|---|
| **SPA** | MSAL Browser / Angular SPAs | PKCE auth code flow — tokens returned directly to browser |
| **Web** | Server-side apps, API callbacks | Auth code flow — tokens returned server-side |

MSAL Angular with `@azure/msal-browser` always uses the **SPA** platform. Adding a URI to **Web** instead will cause `redirect_uri_mismatch` errors at runtime.

---

## `redirectUri` in MSAL Config vs App Registration

The `redirectUri` in `MSALInstanceFactory` must **exactly match** one of the registered SPA URIs in Azure AD (including trailing slash).

```typescript
// environment.ts
redirectUri: '/',  // resolves to http://localhost:4200/

// Azure AD must have: "http://localhost:4200/" (WITH trailing slash)
// OR:                 "http://localhost:4200"  (WITHOUT — Azure is lenient about trailing slash)
```

If you see `AADSTS50011: The redirect URI ... does not match`, check:

1. Is the URI in the **SPA** section (not Web)?
2. Does the scheme, host, port, and path match exactly?
3. Is `http://` used for localhost (not `https://`)?

Back to the index: [msal-angular-appreg](msal-angular-appreg.md)
