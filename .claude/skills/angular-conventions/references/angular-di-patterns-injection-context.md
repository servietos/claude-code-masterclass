# Injection Context Utilities

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
Back to the index: [angular-di-patterns](angular-di-patterns.md)
