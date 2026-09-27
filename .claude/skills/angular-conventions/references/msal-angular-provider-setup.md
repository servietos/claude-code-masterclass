# MSAL Angular provider setup (msal.auth.ts)

## Provider Setup (`msal.auth.ts`)

```typescript
import { APP_INITIALIZER } from '@angular/core';
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import {
  MsalInterceptorConfiguration, MsalGuardConfiguration, MsalInterceptor,
  MSAL_INSTANCE, MSAL_GUARD_CONFIG, MSAL_INTERCEPTOR_CONFIG,
  MsalService, MsalGuard, MsalBroadcastService,
} from '@azure/msal-angular';
import {
  LogLevel, IPublicClientApplication, PublicClientApplication,
  BrowserCacheLocation, InteractionType,
} from '@azure/msal-browser';
import { firstValueFrom } from 'rxjs';

export function MSALInstanceFactory(): IPublicClientApplication {
  return new PublicClientApplication({
    auth: {
      clientId: environment.azure.msalConfig.auth.clientId,
      authority: environment.azure.msalConfig.auth.authority,
      redirectUri: environment.azure.msalConfig.auth.redirectUri, // e.g. '/'
      postLogoutRedirectUri: environment.azure.msalConfig.auth.redirectUri,
      // DO NOT add navigateToLoginRequestUrl here: removed from config in v5.
      // It moved onto the call: handleRedirectObservable({ navigateToLoginRequestUrl: false })
    },
    cache: { cacheLocation: BrowserCacheLocation.LocalStorage },
    system: {
      allowPlatformBroker: false, // REQUIRED on Windows — disables WAM broker
      loggerOptions: { ... },
    },
  });
}

export function MSALInterceptorConfigFactory(): MsalInterceptorConfiguration {
  const protectedResourceMap = new Map<string, Array<string>>();
  protectedResourceMap.set(`${environment.apiUrl}/api/*`, environment.azure.protectedScopes);
  return {
    interactionType: InteractionType.Redirect, // match the guard
    protectedResourceMap,
  };
}

export function MSALGuardConfigFactory(): MsalGuardConfiguration {
  return {
    interactionType: InteractionType.Redirect, // match the interceptor
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

**Why `APP_INITIALIZER`?** It ensures MSAL is fully initialized (via `handleRedirectObservable()`) before Angular routes activate. Without it, the `MsalGuard` may run against an uninitialized `PublicClientApplication`, or a redirect response (`#code=...`) can be stripped by the router before MSAL reads it.

**Do NOT also call `handleRedirectObservable()` in `AuthStateService`** — `APP_INITIALIZER` is the single owner.


Back to the index: [msal-angular](msal-angular.md)
