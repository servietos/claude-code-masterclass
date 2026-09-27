# Standalone bootstrap: no MsalRedirectComponent

## `MsalRedirectComponent` — NOT for Standalone

The docs are explicit:

> "This approach is not compatible with Angular standalone components."

Do **not** do:

```typescript
// WRONG for standalone
bootstrapApplication(MsalRedirectComponent, appConfig);
```

```html
<!-- WRONG — remove if present -->
<app-redirect></app-redirect>
```

The `APP_INITIALIZER` pattern above replaces `MsalRedirectComponent` for standalone apps.


## `main.ts` — Single Bootstrap Only

```typescript
import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { App } from './app/app';

bootstrapApplication(App, appConfig).catch(err => console.error(err));
// No second bootstrapApplication(MsalRedirectComponent) — not for standalone
```


## `app.config.ts` Pattern

```typescript
export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes, withComponentInputBinding()),
    provideHttpClient(withInterceptorsFromDi(), withFetch()),
    AppStore,
    ...(environment.authEnabled ? msalServiceProviders : []),
  ],
};
```

Conditionally loading providers via `authEnabled` flag is fine — MSAL tokens and interceptors are only registered when auth is enabled.


Back to the index: [msal-angular](msal-angular.md)
