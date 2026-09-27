# Injection Context: Environment Injectors and Custom inject Helpers

## Environment Injector

Create injectors programmatically:

```typescript
import { createEnvironmentInjector, EnvironmentInjector, inject } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class Plugin {
  private parentInjector = inject(EnvironmentInjector);
  
  loadPlugin(providers: Provider[]): EnvironmentInjector {
    return createEnvironmentInjector(providers, this.parentInjector);
  }
}
```

## runInInjectionContext

Run code with injection context:

```typescript
import { runInInjectionContext, EnvironmentInjector, inject } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class Utility {
  private injector = inject(EnvironmentInjector);
  
  executeWithDI<T>(fn: () => T): T {
    return runInInjectionContext(this.injector, fn);
  }
}

// Usage
utilityService.executeWithDI(() => {
  const http = inject(HttpClient);
  // Use http...
});
```

## Injection Context Utilities

### assertInInjectionContext

```typescript
import { assertInInjectionContext, inject } from '@angular/core';

export function injectLogger(): Logger {
  assertInInjectionContext(injectLogger);
  return inject(Logger);
}

// Usage - must be called in injection context
@Component({...})
export class My2 {
  private logger = injectLogger(); // OK

  someMethod() {
    // injectLogger(); // ERROR - not in injection context
  }
}
```

### Custom inject Functions

```typescript
// Create reusable injection utilities
export function injectRouteParam(param: string): Signal<string | null> {
  assertInInjectionContext(injectRouteParam);
  
  const route = inject(ActivatedRoute);
  return toSignal(
    route.paramMap.pipe(map(params => params.get(param))),
    { initialValue: null }
  );
}

export function injectQueryParam(param: string): Signal<string | null> {
  assertInInjectionContext(injectQueryParam);
  
  const route = inject(ActivatedRoute);
  return toSignal(
    route.queryParamMap.pipe(map(params => params.get(param))),
    { initialValue: null }
  );
}

// Usage
@Component({...})
export class UserCmpt {
  userId = injectRouteParam('id');
  tab = injectQueryParam('tab');
}
```

Back to the index: [angular-di](angular-di.md)
