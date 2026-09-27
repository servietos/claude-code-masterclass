# Route Configuration Reference

## Route Configuration Options

### Full Route Options

```typescript
{
  path: 'users/:id',
  component: UserCmpt,
  
  // Lazy loading alternatives
  loadComponent: () => import('./user.component').then(m => m.UserCmpt),
  loadChildren: () => import('./user.routes').then(m => m.userRoutes),
  
  // Guards
  canActivate: [authGuard],
  canActivateChild: [authGuard],
  canDeactivate: [unsavedChangesGuard],
  canMatch: [featureFlagGuard],
  
  // Data
  resolve: { user: userResolver },
  data: { title: 'User Profile', animation: 'userPage' },
  
  // Children
  children: [...],
  
  // Outlet
  outlet: 'sidebar',
  
  // Path matching
  pathMatch: 'full', // or 'prefix'
  
  // Title
  title: 'User Profile',
  // Or dynamic title
  title: userTitleResolver,
}
```

### Dynamic Title Resolver

```typescript
export const userTitleResolver: ResolveFn<string> = (route) => {
  const userService = inject(User);
  const id = route.paramMap.get('id')!;
  return userService.getById(id).pipe(
    map(user => `${user.name} - Profile`)
  );
};
```

Back to the index: [angular-routing](angular-routing.md)
