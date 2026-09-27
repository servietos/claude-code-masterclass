# app.config.ts registration

## `app.config.ts` Registration

```typescript
import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptorsFromDi, withFetch } from '@angular/common/http';
import { msalServiceProviders } from './auth/msal.auth';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(withInterceptorsFromDi(), withFetch()), // withInterceptorsFromDi() required for MsalInterceptor
    ...(environment.authEnabled ? msalServiceProviders : []),
  ],
};
```

`withInterceptorsFromDi()` is **required** because `MsalInterceptor` is registered via the class-based `HTTP_INTERCEPTORS` token. Without it, the interceptor is silently dropped and no bearer token is attached.

Back to the index: [angular-msal-auth](angular-msal-auth.md)
