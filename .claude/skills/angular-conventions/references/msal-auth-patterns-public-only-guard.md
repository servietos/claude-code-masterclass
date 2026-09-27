# publicOnlyGuard: redirect signed-in users off public routes

## Guard pattern: redirect authenticated users away from public/landing routes

The inverse of `authGuard`. Put it on a public landing route (`path: ''`) so a signed-in user is
sent straight to the app shell (e.g. `/dashboard`) and never sees the marketing/login view:

```typescript
export const publicOnlyGuard: CanActivateFn = async () => {
  if (!environment.authEnabled) return true;
  const auth = inject(AuthService); const router = inject(Router);
  await auth.whenReady();                                   // or ensureInitialized()
  return auth.isLoggedIn() ? router.createUrlTree(['/dashboard']) : true;
};
```

Pair it with hiding the public nav links when `auth.isLoggedIn()` (`@if (!authEnabled || !auth.isLoggedIn())`)
so the logged-in shell stays clean.

Back to the index: [msal-auth-patterns](msal-auth-patterns.md)
