# Injection and Component Communication

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

## Component Communication Patterns

### Parent to Child (Inputs)

```typescript
// Parent
@Component({
  template: `<app-child [data]="parentData()" [config]="config" />`,
})
export class Parent {
  parentData = signal({ name: 'Test' });
  config = { theme: 'dark' };
}

// Child
@Component({ selector: 'app-child' })
export class Child {
  data = input.required<Data>();
  config = input<Config>();
}
```

### Child to Parent (Outputs)

```typescript
// Child
@Component({
  selector: 'app-child',
  template: `<button (click)="save()">Save</button>`,
})
export class Child {
  saved = output<Data>();
  
  save() {
    this.saved.emit({ id: 1, name: 'Item' });
  }
}

// Parent
@Component({
  template: `<app-child (saved)="onSaved($event)" />`,
})
export class Parent {
  onSaved(data: Data) {
    console.log('Saved:', data);
  }
}
```

### Shared Service Pattern

```typescript
// Shared state service
@Injectable({ providedIn: 'root' })
export class Cart {
  private items = signal<CartItem[]>([]);
  
  readonly items$ = this.items.asReadonly();
  readonly total = computed(() => 
    this.items().reduce((sum, item) => sum + item.price, 0)
  );
  
  addItem(item: CartItem) {
    this.items.update(items => [...items, item]);
  }
  
  removeItem(id: string) {
    this.items.update(items => items.filter(i => i.id !== id));
  }
}

// Component A
@Component({ template: `<button (click)="add()">Add</button>` })
export class Product {
  private cart = inject(Cart);
  product = input.required<Product>();
  
  add() {
    this.cart.addItem({ ...this.product(), quantity: 1 });
  }
}

// Component B
@Component({ template: `<span>Total: {{ cart.total() }}</span>` })
export class CartSummary {
  cart = inject(Cart);
}
```

Back to the index: [angular-component-patterns](angular-component-patterns.md)
