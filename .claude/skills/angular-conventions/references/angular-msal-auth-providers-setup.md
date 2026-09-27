# MSAL environment config and provider factory

## Environment Configuration

```typescript
// environment.ts / environment.prod.ts
export const environment = {
  apiUrl: 'https://your-api.azurewebsites.net',
  authEnabled: true,
  azure: {
    msalConfig: {
      auth: {
        clientId: '<SPA clientId>',
        authority: 'https://login.microsoftonline.com/<tenantId>/',
        redirectUri: '/',
      },
    },
    protectedScopes: ['api://<clientId>/access_as_user'],
  },
};
```

## MSAL Providers Factory

```typescript
// msal.auth.ts
import { APP_INITIALIZER } from '@angular/core';
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import {
  MsalInterceptorConfiguration,
  MsalGuardConfiguration,
  MsalInterceptor,
  MSAL_INSTANCE,
  MSAL_GUARD_CONFIG,
  MSAL_INTERCEPTOR_CONFIG,
  MsalService,
  MsalGuard,
  MsalBroadcastService,
} from '@azure/msal-angular';
import {
  PublicClientApplication,
  BrowserCacheLocation,
  InteractionType,
} from '@azure/msal-browser';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../environments/environment';

export function MSALInstanceFactory() {
  return new PublicClientApplication({
    auth: {
      clientId: environment.azure.msalConfig.auth.clientId,
      authority: environment.azure.msalConfig.auth.authority,
      redirectUri: environment.azure.msalConfig.auth.redirectUri,
      postLogoutRedirectUri: environment.azure.msalConfig.auth.redirectUri,
      // DO NOT add navigateToLoginRequestUrl here — in msal-browser/angular v5 it is
      // NOT set here, it moved to handleRedirectObservable() options. Set it false there
      // when login can start from the same URL as redirectUri (e.g. a landing page
      // with redirectUri '/'), or the redirect return hangs on `/?state=...`.
    },
    cache: { cacheLocation: BrowserCacheLocation.LocalStorage },
    system: {
      allowPlatformBroker: false, // REQUIRED on Windows — disables WAM broker
    },
  });
}

export function MSALInterceptorConfigFactory(): MsalInterceptorConfiguration {
  const protectedResourceMap = new Map<string, Array<string>>();
  // Key MUST end with /api/* — the trailing wildcard is required. MSAL v5 has
  // strictMatching ON by default, so `${apiUrl}/api/` (no wildcard) matches ONLY
  // the exact URL `/api/`, never `/api/inventory` → no token attached → 401.
  protectedResourceMap.set(`${environment.apiUrl}/api/*`, environment.azure.protectedScopes);
  return {
    interactionType: InteractionType.Redirect,
    protectedResourceMap,
  };
}

export function MSALGuardConfigFactory(): MsalGuardConfiguration {
  return {
    interactionType: InteractionType.Redirect,
    authRequest: { scopes: environment.azure.protectedScopes },
    loginFailedRoute: '/login-failed',
  };
}

function msalInitializerFactory(msalService: MsalService) {
  return () => firstValueFrom(msalService.handleRedirectObservable(), { defaultValue: null });
}

export const msalServiceProviders = [
  { provide: HTTP_INTERCEPTORS, useClass: MsalInterceptor, multi: true },
  { provide: MSAL_INSTANCE, useFactory: MSALInstanceFactory },
  { provide: MSAL_GUARD_CONFIG, useFactory: MSALGuardConfigFactory },
  { provide: MSAL_INTERCEPTOR_CONFIG, useFactory: MSALInterceptorConfigFactory },
  MsalService,
  MsalGuard,
  MsalBroadcastService,
  {
    provide: APP_INITIALIZER,
    useFactory: msalInitializerFactory,
    deps: [MsalService],
    multi: true,
  },
];
```

Back to the index: [angular-msal-auth](angular-msal-auth.md)
