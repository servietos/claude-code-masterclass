# MSAL auth on Azure App Service

## Do NOT Enable Easy Auth Alongside Microsoft.Identity.Web

App Service Easy Auth and `Microsoft.Identity.Web` must never coexist. Easy Auth intercepts all requests before ASP.NET Core sees them. Even setting `unauthenticatedClientAction` to `AllowAnonymous` is not enough when the config is in a broken state.

If Easy Auth is stuck enabled and cannot be disabled via CLI, delete and recreate the App Service.

## App Service Settings

When deploying to Azure App Service, set the `AzureAd__*` settings (double underscore = nested config path):

```bash
az webapp config appsettings set -g <rg> -n <app> --settings \
  "AzureAd__Instance=https://login.microsoftonline.com/" \
  "AzureAd__TenantId=<tenantId>" \
  "AzureAd__ClientId=<clientId>" \
  "AzureAd__Audience=<clientId>"
```

These override `appsettings.json` values at runtime. They are not required if `appsettings.json`
already carries the correct values, but setting both does no harm.


Back to the index: [dotnet-msal-auth](dotnet-msal-auth.md)
