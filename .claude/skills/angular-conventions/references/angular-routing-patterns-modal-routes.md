# Modal Routes via Auxiliary Outlets

## Modal Routes

Using auxiliary outlets for modals:

```typescript
// Routes
export const routes: Routes = [
  { path: 'products', component: ProductList },
  { path: 'product-modal/:id', component: ProductModal, outlet: 'modal' },
];

// App template
@Component({
  template: `
    <router-outlet />
    <router-outlet name="modal" />
  `,
})
export class App {}

// Open modal
this.router.navigate([{ outlets: { modal: ['product-modal', productId] } }]);

// Close modal
this.router.navigate([{ outlets: { modal: null } }]);

// Link to open modal
<a [routerLink]="[{ outlets: { modal: ['product-modal', product.id] } }]">
  View Details
</a>
```

Back to the index: [angular-routing-patterns](angular-routing-patterns.md)
