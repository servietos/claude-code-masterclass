# MSAL bootstrap: cached AuthService, startup init, functional authGuard

## Bootstrapping: AuthService + functional guard (recommended)

Prefer a small `AuthService` with a cached `ensureInitialized()` over `MsalGuard`'s
auto-login when you want a public login page and full control of post-login navigation.
**The critical rule: something must call `ensureInitialized()` at startup (the root
component) or the guard's observable never resolves and the app renders a blank page.**
This is the #1 cause of a "blank screen the moment auth is enabled" — it stays dormant
while `authEnabled=false` (the guard short-circuits) and only bites when you flip it on.

```typescript
// auth.service.ts
@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly msal = inject(MsalService, { optional: true });
  private cachedInit$?: Observable<void>;

  ensureInitialized(): Observable<void> {
    if (!this.msal) return of(undefined);                   // auth disabled / no MSAL providers
    this.cachedInit$ ??= this.msal.initialize().pipe(       // v5 REQUIRES initialize() first
      concatMap(() => this.msal!.handleRedirectObservable()),
      tap((r) => { if (r?.account) this.msal!.instance.setActiveAccount(r.account); }),
      map(() => undefined),
      shareReplay(1),                                        // run once; replay to guard + root
    );
    return this.cachedInit$;
  }

  login(): void {
    this.msal?.loginRedirect({ scopes: environment.azure.protectedScopes })
      .subscribe({ error: (e) => console.error('loginRedirect failed', e) });
  }
  logout(): void {
    this.msal?.logoutRedirect()
      .subscribe({ error: (e) => console.error('logoutRedirect failed', e) });
  }
}
```

```typescript
// app.ts — call it ONCE at startup; gate routing on completion
export class App {
  private readonly auth = inject(AuthService);
  protected readonly ready = signal(false);
  constructor() {
    this.auth.ensureInitialized().subscribe({ next: () => this.ready.set(true), error: () => this.ready.set(true) });
  }
}
// app.html:  @if (ready()) { <router-outlet /> } @else { <div class="auth-splash">…</div> }
```

```typescript
// auth.guard.ts — functional, reuses the cached init
export const authGuard: CanActivateFn = () => {
  if (!environment.authEnabled) return true;               // toggle: pass through when disabled
  const auth = inject(AuthService); const router = inject(Router);
  return auth.ensureInitialized().pipe(map(() => (auth.isAuthenticated() ? true : router.createUrlTree(['/login']))));
};
```

Read the signed-in user from the MSAL `AccountInfo` (`account.name` / `account.username`).
**Do NOT call a `/api/auth/me` endpoint unless one actually exists** — a 404 there will clear
the user right after a successful login and bounce the guard straight back to `/login`.

## See Also

- [`angular-msal-auth.md`](angular-msal-auth.md) - provider wiring the patterns here assume
- [`msal-troubleshooting.md`](msal-troubleshooting.md) - blank page, redirect loop, 401 triage
- [`msal-angular.md`](msal-angular.md) - `AuthStateService`, `MsalRedirectComponent`, bootstrap rules

Back to the index: [msal-auth-patterns](msal-auth-patterns.md)
