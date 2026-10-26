# MSAL auth: app registration and package prerequisites

> **Package version.** Stay on the latest `Microsoft.Identity.Web` 4.x (current stable **4.11.0**, 2026-06).
> Minor bumps across the 4.x line are non-breaking — no public-API or config changes to `AddMicrosoftIdentityWebApi` —
> so a straight `<PackageReference Version="…">` bump + `dotnet restore`/`build` is safe. No companion
> `Microsoft.Identity.Client` / `Microsoft.Identity.Web.UI` references are needed for a bearer-token API.

## App Registration Requirements

| Setting | Required value | Why |
|---|---|---|
| `api.requestedAccessTokenVersion` | `2` | Default (null) issues v1 tokens with issuer `https://sts.windows.net/{tenantId}/`; `Microsoft.Identity.Web` validates the v2 issuer, causing 401 |
| `appRoles` | one entry per role any policy names | A `RequireRole("Owner")` policy against `appRoles: []` yields a clean sign-in followed by 403 on every call, which reads like an audience or scope bug and is neither |
| `spa.redirectUris` | every host the SPA is served from | Missing host gives `AADSTS50011` at sign-in, before any API call |

Check and fix:

```bash
az ad app show --id <clientId> --query "api.requestedAccessTokenVersion" -o tsv
# Must return 2. If null:
az ad app update --id <clientId> --set "api={'requestedAccessTokenVersion': 2}"

# Roles and redirect URIs in one read, before flipping AuthEnabled:
az ad app show --id <clientId> --query "{roles:appRoles[].value,spa:spa.redirectUris}"
```

Adding an app role is a Graph PATCH on the **application object id**, not the client id, and each role
needs a fresh GUID you generate. Assigning it is a second call against the **service principal**:

```bash
az rest --method PATCH --uri "https://graph.microsoft.com/v1.0/applications/<objectId>" \
  --headers "Content-Type=application/json" --body @roles.json
az rest --method POST \
  --uri "https://graph.microsoft.com/v1.0/servicePrincipals/<spId>/appRoleAssignedTo" \
  --headers "Content-Type=application/json" \
  --body '{"principalId":"<userObjectId>","resourceId":"<spId>","appRoleId":"<roleGuid>"}'
```

## Activation order: identity before the switch

Flipping `AuthEnabled` to true is the LAST step, not the first. Two traps, both seen together on
2026-09-06 activating `secrets-mcp`:

- **Seed the data first when the service is both the auth subject and the data-entry API.** Writing
  configuration into a store through that store's own REST API stops working the moment its policies
  turn on, and you cannot get a token until the roles exist. Order is: seed, then roles, then flip.
- **An `X-API-Key` scheme is not a fallback for the SPA policy.** A dual-scheme server usually maps the
  machine key to its own policies only; the SPA controllers stay JWT-and-role. Worse, a repo whose
  `Mcp:ApiKeys[].Key` is `""` in `appsettings.Development.json` (the real key living in the secrets
  store) fails the key check closed, so the machine path 401s too and nothing can write.

Back to the index: [dotnet-msal-auth](dotnet-msal-auth.md)
