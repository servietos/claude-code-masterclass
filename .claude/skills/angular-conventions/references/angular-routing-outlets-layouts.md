# Nested Routes, Tabs and Modal Outlets

## Nested Routes

```typescript
// Parent route with children
export const routes: Routes = [
  {
    path: 'products',
    component: ProductsLayout,
    children: [
      { path: '', component: ProductList },
      { path: ':id', component: ProductDetail },
      { path: ':id/edit', component: ProductEdit },
    ],
  },
];

// ProductsLayout
@Component({
  imports: [RouterOutlet],
  template: `
    <h1>Products</h1>
    <router-outlet /> <!-- Child routes render here -->
  `,
})
export class ProductsLayout {}
```

## Tab Navigation

```typescript
// tabs-layout.component.ts
@Component({
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <div class="tabs">
      @for (tab of tabs; track tab.path) {
        <a 
          [routerLink]="tab.path" 
          routerLinkActive="active"
          [routerLinkActiveOptions]="{ exact: tab.exact }"
        >
          {{ tab.label }}
        </a>
      }
    </div>
    <div class="tab-content">
      <router-outlet />
    </div>
  `,
})
export class TabsLayout {
  tabs = [
    { path: './', label: 'Overview', exact: true },
    { path: 'details', label: 'Details', exact: false },
    { path: 'settings', label: 'Settings', exact: false },
  ];
}

// Routes
{
  path: 'account',
  component: TabsLayout,
  children: [
    { path: '', component: AccountOverview },
    { path: 'details', component: AccountDetails },
    { path: 'settings', component: AccountSettings },
  ],
}
```

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

Back to the index: [angular-routing](angular-routing.md)
