# Required registration settings before coding

## Login Required — Azure AD Consent Scopes

The app uses a custom API scope: `api://54f03c51-f41a-4f1f-97ca-d219ee28ee50/access_as_user`

This scope must be exposed in the **Expose an API** section of the app registration. If users see "Need admin approval" errors, the scope may not be pre-consented for the tenant.

---

## App Registration Requirements

Before writing any code, verify the Entra app registration:

| Setting | Required value | Why |
|---|---|---|
| `api.requestedAccessTokenVersion` | `2` | Null (default) issues v1 tokens; `Microsoft.Identity.Web` validates the v2 issuer and rejects them, causing 401 |
| SPA redirect URIs | Must be under **SPA** platform (not Web) | Web platform issues auth codes incompatible with PKCE flows |
| `web.implicitGrantSettings.enableAccessTokenIssuance` | `false` | Implicit flow is obsolete; SPA platform uses auth code + PKCE |

Check with:

```bash
az ad app show --id <clientId> --query "api.requestedAccessTokenVersion" -o tsv
# Must return 2. If null, fix:
az ad app update --id <clientId> --set "api={'requestedAccessTokenVersion': 2}"
```

---

## Related

- [`msal-angular.md`](msal-angular.md) — provider setup and auth service patterns
- [`angular-msal-auth.md`](angular-msal-auth.md) — MSAL overview and 401 triage

Back to the index: [msal-angular-appreg](msal-angular-appreg.md)
