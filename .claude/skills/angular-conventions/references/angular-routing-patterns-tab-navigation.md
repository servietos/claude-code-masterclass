# Tab Shell with Child Routes

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

Back to the index: [angular-routing-patterns](angular-routing-patterns.md)
