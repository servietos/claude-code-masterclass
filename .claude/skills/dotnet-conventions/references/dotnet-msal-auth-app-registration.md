# MSAL auth: app registration and package prerequisites

> **Package version.** Stay on the latest `Microsoft.Identity.Web` 4.x (current stable **4.11.0**, 2026-06).
> Minor bumps across the 4.x line are non-breaking — no public-API or config changes to `AddMicrosoftIdentityWebApi` —
> so a straight `<PackageReference Version="…">` bump + `dotnet restore`/`build` is safe. No companion
> `Microsoft.Identity.Client` / `Microsoft.Identity.Web.UI` references are needed for a bearer-token API.

## App Registration Requirements

| Setting | Required value | Why |
|---|---|---|
| `api.requestedAccessTokenVersion` | `2` | Default (null) issues v1 tokens with issuer `https://sts.windows.net/{tenantId}/`; `Microsoft.Identity.Web` validates the v2 issuer, causing 401 |

Check and fix:

```bash
az ad app show --id <clientId> --query "api.requestedAccessTokenVersion" -o tsv
# Must return 2. If null:
az ad app update --id <clientId> --set "api={'requestedAccessTokenVersion': 2}"
```

Back to the index: [dotnet-msal-auth](dotnet-msal-auth.md)
