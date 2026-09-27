# Angular Dependency Injection

Configure and use dependency injection in Angular v20+ with `inject()` and providers.

> Prefer `inject()` over constructor injection:

| You want to... | Read |
| --- | --- |
| Inject a dependency, write an injectable service | [inject-basics](angular-di-inject-basics.md) |
| Know which injector serves an instance, who shares it | [provider-scopes](angular-di-provider-scopes.md) |
| Inject a non-class value: URL, config, window | [injection-tokens](angular-di-injection-tokens.md) |
| Pick useClass, useValue, useFactory, useExisting | [provider-types](angular-di-provider-types.md) |
| Register many values under one token | [multi-providers](angular-di-multi-providers.md) |
| Make a lookup optional, or start/stop it somewhere | [injection-options](angular-di-injection-options.md) |
| Run async work before the app starts | [app-initializers](angular-di-app-initializers.md) |
| Use inject() outside a constructor | [injection-context](angular-di-injection-context.md) |
| Shape a facade, state or repository service | [service-patterns](angular-di-service-patterns.md) |
| Swap an implementation behind a typed contract | [abstract-class-tokens](angular-di-abstract-class-tokens.md) |
| Choose the implementation at runtime | [dynamic-providers](angular-di-dynamic-providers.md) |
| Fake a service or override a provider in tests | [testing](angular-di-testing.md) |
| Clean up on destroy | [destroyref-cleanup](angular-di-destroyref-cleanup.md) |
