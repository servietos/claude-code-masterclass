# Functional Route Guards

## Functional Guards

### Auth Guard

```typescript
// guards/auth.guard.ts
import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(Auth);
  const router = inject(Router);
  
  if (authService.isAuthenticated()) {
    return true;
  }
  
  // Redirect to login with return URL
  return router.createUrlTree(['/login'], {
    queryParams: { returnUrl: state.url },
  });
};

// Usage in routes
{
  path: 'dashboard',
  component: Dashboard,
  canActivate: [authGuard],
}
```

### Role Guard

```typescript
export const roleGuard = (allowedRoles: string[]): CanActivateFn => {
  return (route, state) => {
    const authService = inject(Auth);
    const router = inject(Router);
    
    const userRole = authService.currentUser()?.role;
    
    if (userRole && allowedRoles.includes(userRole)) {
      return true;
    }
    
    return router.createUrlTree(['/unauthorized']);
  };
};

// Usage
{
  path: 'admin',
  component: Admin,
  canActivate: [authGuard, roleGuard(['admin', 'superadmin'])],
}
```

### Can Deactivate Guard

```typescript
export interface CanDeactivate {
  canDeactivate: () => boolean | Promise<boolean>;
}

export const unsavedChangesGuard: CanDeactivateFn<CanDeactivate> = (component) => {
  if (component.canDeactivate()) {
    return true;
  }
  
  return confirm('You have unsaved changes. Leave anyway?');
};

// Component implementation
@Component({...})
export class Edit implements CanDeactivate {
  form = inject(FormBuilder).group({...});
  
  canDeactivate(): boolean {
    return !this.form.dirty;
  }
}

// Route
{
  path: 'edit/:id',
  component: Edit,
  canDeactivate: [unsavedChangesGuard],
}
```

Back to the index: [angular-routing](angular-routing.md)
