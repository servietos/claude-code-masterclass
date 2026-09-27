# Create separate API and SPA registrations

### Creating the registrations via az CLI

Create two app regs — an **API** (exposes the scope) and a **SPA** (consumes it). The scope
is added to the API via a Graph PATCH, then referenced from the SPA's `requiredResourceAccess`.

```bash
az ad app create --display-name "<App> API"   --sign-in-audience AzureADMyOrg   # -> apiAppId, apiObjectId
az ad app create --display-name "<App> Admin" --sign-in-audience AzureADMyOrg   # -> spaAppId, spaObjectId
az ad sp create --id <apiAppId>; az ad sp create --id <spaAppId>                 # service principals
```

Then PATCH `https://graph.microsoft.com/v1.0/applications/<apiObjectId>` with `identifierUris:
["api://<apiAppId>"]` and `api.{ requestedAccessTokenVersion: 2, oauth2PermissionScopes: [{ id:
<newGuid>, value: "access_as_user", type: "User", isEnabled: true, …consent text… }] }`; PATCH
the SPA with `spa.redirectUris: ["http://localhost:4200"]` and `requiredResourceAccess` pointing
at `<apiAppId>` + the scope id (`type: "Scope"`); finally `az ad app permission admin-consent --id <spaAppId>`.

**Gotcha (chicken-and-egg):** do NOT include `api.preAuthorizedApplications` in the same PATCH that
*creates* the `oauth2PermissionScopes` — Graph rejects it (`InvalidValue … Permission Id … cannot be
found`) because the scope doesn't exist yet. Either skip pre-authorization (admin consent covers it)
or add it in a **second** PATCH after the scope exists, reusing the same scope GUID.

Back to the index: [msal-angular-appreg](msal-angular-appreg.md)
