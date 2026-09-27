# Reading Route and Query Parameters

## Route Parameters

### With Signal Inputs (Recommended)

```typescript
// Route config
{ path: 'users/:id', component: UserDetail }

// Component - use input() for route params
import { Component, input, computed } from '@angular/core';

@Component({
  selector: 'app-user-detail',
  template: `
    <h1>User {{ id() }}</h1>
  `,
})
export class UserDetail {
  // Route param as signal input
  id = input.required<string>();
  
  // Computed based on route param
  userId = computed(() => parseInt(this.id(), 10));
}
```

Enable with `withComponentInputBinding()`:

```typescript
// app.config.ts
import { provideRouter, withComponentInputBinding } from '@angular/router';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes, withComponentInputBinding()),
  ],
};
```

### Query Parameters

```typescript
// Route: /search?q=angular&page=1

@Component({...})
export class Search {
  // Query params as inputs
  q = input<string>('');
  page = input<string>('1');
  
  currentPage = computed(() => parseInt(this.page(), 10));
}
```

### With ActivatedRoute (Alternative)

```typescript
import { Component, inject } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs';

@Component({...})
export class UserDetail {
  private route = inject(ActivatedRoute);
  
  // Convert route params to signal
  id = toSignal(
    this.route.paramMap.pipe(map(params => params.get('id'))),
    { initialValue: null }
  );
  
  // Query params
  query = toSignal(
    this.route.queryParamMap.pipe(map(params => params.get('q'))),
    { initialValue: '' }
  );
}
```

Back to the index: [angular-routing](angular-routing.md)
