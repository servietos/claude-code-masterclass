# App Initializers

## App Initializers

Run async code before app starts using `provideAppInitializer`:

```typescript
import { provideAppInitializer, inject } from '@angular/core';

export const appConfig: ApplicationConfig = {
  providers: [
    Config,
    provideAppInitializer(() => {
      const configService = inject(Config);
      return configService.loadConfig();
    }),
  ],
};
```

### Multiple Initializers

```typescript
providers: [
  provideAppInitializer(() => {
    const config = inject(Config);
    return config.load();
  }),
  provideAppInitializer(() => {
    const auth = inject(Auth);
    return auth.checkSession();
  }),
]
```

Back to the index: [angular-di](angular-di.md)
