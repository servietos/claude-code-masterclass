# Provider Types: useClass, useValue, useFactory, useExisting

## Provider Types

### useClass

```typescript
// Provide implementation
{ provide: Logger, useClass: ConsoleLogger }

// Conditional implementation
{
  provide: Logger,
  useClass: environment.production
    ? ProductionLogger
    : ConsoleLogger,
}
```

### useValue

```typescript
// Static values
{ provide: API_URL, useValue: 'https://api.example.com' }

// Configuration objects
{ provide: APP_CONFIG, useValue: { theme: 'dark', language: 'en' } }
```

### useFactory

```typescript
// Factory with dependencies
{
  provide: User,
  useFactory: (http: HttpClient, config: AppConfig) => {
    return new User(http, config.apiUrl);
  },
  deps: [HttpClient, APP_CONFIG],
}

// Async factory (not recommended - use provideAppInitializer)
{
  provide: CONFIG,
  useFactory: () => fetch('/config.json').then(r => r.json()),
}
```

### useExisting

```typescript
// Alias to existing provider
{ provide: AbstractLogger, useExisting: ConsoleLogger }

// Multiple tokens pointing to same instance
providers: [
  ConsoleLogger,
  { provide: Logger, useExisting: ConsoleLogger },
  { provide: ErrorLogger, useExisting: ConsoleLogger },
]
```

Back to the index: [angular-di](angular-di.md)
