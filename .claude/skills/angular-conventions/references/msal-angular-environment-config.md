# environment.ts MSAL values

## `environment.ts` — Project MSAL Config

```typescript
export const environment = {
  production: false,
  apiUrl: 'https://localhost:5001',
  authEnabled: true,
  azure: {
    msalConfig: {
      auth: {
        clientId: '54f03c51-f41a-4f1f-97ca-d219ee28ee50',
        authority: 'https://login.microsoftonline.com/d92b247e-90e0-4469-a129-6a32866c0d0a/',
        redirectUri: '/',                 // resolves to http://localhost:4200/ — must match SPA redirect URI in Azure AD
      },
    },
    protectedScopes: ['api://54f03c51-f41a-4f1f-97ca-d219ee28ee50/access_as_user'],
  },
};
```

Key values:

| Property | Value |
|---|---|
| `clientId` | `54f03c51-f41a-4f1f-97ca-d219ee28ee50` |
| `authority` | `https://login.microsoftonline.com/d92b247e-90e0-4469-a129-6a32866c0d0a/` |
| `redirectUri` | `/` (resolves to `http://localhost:4200/` in dev) |
| `protectedScopes` | `api://54f03c51-f41a-4f1f-97ca-d219ee28ee50/access_as_user` |

The `protectedScopes` value is also the `access_as_user` scope exposed in **Expose an API** in the app registration — see `msal-angular-appreg.md`.


Back to the index: [msal-angular](msal-angular.md)
