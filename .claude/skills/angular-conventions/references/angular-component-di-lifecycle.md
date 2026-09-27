# inject() and component lifecycle

## Dependency Injection in Components

Use `inject()` function instead of constructor injection:

```typescript
import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-dashboard',
  template: `...`,
})
export class Dashboard {
  private router = inject(Router);
  private userService = inject(User);
  private config = inject(APP_CONFIG);
  
  // Optional injection
  private analytics = inject(Analytics, { optional: true });
  
  // Self-only injection
  private localService = inject(Local, { self: true });
  
  navigateToProfile() {
    this.router.navigate(['/profile']);
  }
}
```

## Lifecycle Hooks

```typescript
import { OnDestroy, OnInit, afterNextRender, afterRender } from '@angular/core';

export class My implements OnInit, OnDestroy {
  constructor() {
    // For DOM manipulation after render (SSR-safe)
    afterNextRender(() => {
      // Runs once after first render
    });

    afterRender(() => {
      // Runs after every render
    });
  }

  ngOnInit() { /* Component initialized */ }
  ngOnDestroy() { /* Cleanup */ }
}
```

Back to the index: [angular-component](angular-component.md)
