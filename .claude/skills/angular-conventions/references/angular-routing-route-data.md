# Resolvers and Static Route Data

## Resolvers

Pre-fetch data before route activation:

```typescript
// resolvers/user.resolver.ts
import { inject } from '@angular/core';
import { ResolveFn } from '@angular/router';

export const userResolver: ResolveFn<User> = (route) => {
  const userService = inject(User);
  const id = route.paramMap.get('id')!;
  return userService.getById(id);
};

// Route config
{
  path: 'users/:id',
  component: UserDetail,
  resolve: { user: userResolver },
}

// Component - access resolved data via input
@Component({...})
export class UserDetail {
  user = input.required<User>();
}
```

## Route Data

```typescript
// Static route data
{
  path: 'admin',
  component: Admin,
  data: {
    title: 'Admin Dashboard',
    roles: ['admin'],
  },
}

// Access in component
@Component({...})
export class AdminCmpt {
  title = input<string>(); // From route data
  roles = input<string[]>(); // From route data
}

// Or via ActivatedRoute
private route = inject(ActivatedRoute);
data = toSignal(this.route.data);
```

Back to the index: [angular-routing](angular-routing.md)
