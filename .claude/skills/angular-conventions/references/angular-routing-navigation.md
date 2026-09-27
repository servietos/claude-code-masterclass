# Programmatic Navigation and Router Events

## Programmatic Navigation

```typescript
import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';

@Component({...})
export class Product {
  private router = inject(Router);
  
  // Navigate to route
  goToProducts() {
    this.router.navigate(['/products']);
  }
  
  // Navigate with params
  goToProduct(id: string) {
    this.router.navigate(['/products', id]);
  }
  
  // Navigate with query params
  search(query: string) {
    this.router.navigate(['/search'], {
      queryParams: { q: query, page: 1 },
    });
  }
  
  // Navigate relative to current route
  goToEdit() {
    this.router.navigate(['edit'], { relativeTo: this.route });
  }
  
  // Replace current history entry
  replaceUrl() {
    this.router.navigate(['/new-page'], { replaceUrl: true });
  }
}
```

## Router Events

```typescript
import { Router, NavigationStart, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs';

@Component({...})
export class AppMain {
  private router = inject(Router);
  
  isNavigating = signal(false);
  
  constructor() {
    this.router.events.pipe(
      filter(e => e instanceof NavigationStart || e instanceof NavigationEnd)
    ).subscribe(event => {
      this.isNavigating.set(event instanceof NavigationStart);
    });
  }
}
```

Back to the index: [angular-routing](angular-routing.md)
