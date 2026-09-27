# Localhost port ambiguity and AADSTS9002326

## Localhost: the port is NOT part of the URI's identity

Per [the reply-url doc](https://learn.microsoft.com/entra/identity-platform/reply-url#localhost-exceptions), for **localhost only**, the port component is ignored when matching a redirect URI. `https://localhost:4200`, `https://localhost:5001` and `https://localhost:7071` are all **the same URI** to the login server. Scheme still counts; port does not.

The consequence is the trap, quoted from the doc:

> Do not register multiple localhost redirect URIs where only the port differs. **The login server picks one arbitrarily and uses the behavior associated with that registered redirect URI** (for example, whether it's a `web`-, `native`-, or `spa`-type redirect).

So a single app registration that serves both an API (`https://localhost:5001` on **Web**) and a SPA dev server (`https://localhost:4200` on **SPA**) has one ambiguous `https://localhost` entry with two platform types. When the login server picks the `web` one, the browser's code-to-token call is refused:

```
AADSTS9002326: Cross-origin token redemption is permitted only for the
'Single-Page Application' client-type. Request origin: 'https://localhost:4200'
```

**This fires at the token exchange, not at `/authorize`** — sign-in completes, the app lands back on its redirect URI, then bootstrap dies. `handleRedirectObservable` in an `APP_INITIALIZER` rejects, so the symptom is a blank page plus that error in the console.

Rules:

- An `http://localhost:4200` SPA URI does **not** collide with `https://localhost:5001` on Web: the schemes differ. This is usually why a dev login works on http and breaks the moment the dev server is switched to https.
- Never register a band of localhost ports "to be safe" (`4200`–`4210`). Every entry is the same URI; you are stacking ambiguity, not coverage.
- To run more than one localhost flow off one registration, differentiate by **path**: `https://localhost/MyWebApp` does not match `https://localhost/MyNativeApp`. Set MSAL's `redirectUri` to that path and give the SPA a route for it.
- Audit all three platforms together before adding anything:

```bash
az ad app show --id <appId> \
  --query "{spa:spa.redirectUris, web:web.redirectUris, publicClient:publicClient.redirectUris}" -o json
```

### Do not "verify" a redirect URI by probing the token endpoint

POSTing to `/oauth2/v2.0/token` with an `Origin` header and a fake `code` proves nothing: the malformed code short-circuits with `AADSTS9002313` **before** the cross-origin check runs, so a deliberately unregistered origin returns exactly the same response as a registered one. If you try it anyway, always run the same probe against a known-bad origin first; identical output means the probe discriminates nothing.

Back to the index: [msal-angular-appreg](msal-angular-appreg.md)
