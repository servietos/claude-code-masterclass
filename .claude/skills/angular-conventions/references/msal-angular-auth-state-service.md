# AuthStateService: events, login, logout

## `AuthStateService` — Auth State Pattern

```typescript
@Injectable({ providedIn: 'root' })
export class AuthStateService {
  private readonly msalGuardConfig = inject<MsalGuardConfiguration>(MSAL_GUARD_CONFIG);
  private readonly authService = inject(MsalService);
  private readonly msalBroadcastService = inject(MsalBroadcastService);
  private readonly router = inject(Router);

  loggedInUserEMail = signal('');

  constructor() {
    // Listen for login/logout events
    this.msalBroadcastService.msalSubject$.pipe(
      filter((msg: EventMessage) =>
        msg.eventType === EventType.LOGIN_SUCCESS ||   // was ACCOUNT_ADDED in v4
        msg.eventType === EventType.LOGOUT_SUCCESS,    // was ACCOUNT_REMOVED in v4
      ),
    ).subscribe(() => {
      if (this.authService.instance.getAllAccounts().length === 0) {
        window.location.pathname = '/';
      }
    });

    // Set active account when interaction completes
    this.msalBroadcastService.inProgress$.pipe(
      filter((status: InteractionStatus) => status === InteractionStatus.None),
    ).subscribe(() => {
      const account =
        this.authService.instance.getActiveAccount() ??
        this.authService.instance.getAllAccounts()[0];
      if (account) {
        this.authService.instance.setActiveAccount(account);
        this.loggedInUserEMail.set(account.username);
        if (this.router.url === '/') this.router.navigate(['/vouchers']);
      } else {
        this.loggedInUserEMail.set('');
      }
    });
  }

  login() {
    // Use loginRedirect — loginPopup has cross-window session storage issues
    if (this.msalGuardConfig.authRequest) {
      this.authService.loginRedirect({ ...this.msalGuardConfig.authRequest } as RedirectRequest);
    } else {
      this.authService.loginRedirect();
    }
  }

  logout() {
    this.authService.logoutRedirect(); // logout() removed in MSAL Angular v5
    this.loggedInUserEMail.set('');
  }
}
```

> **Local-only logout (no Microsoft round-trip).** `logoutRedirect()` always navigates to the
> Entra end-session endpoint (and, with no account, shows a "pick an account to sign out" page).
> For a purely local sign-out — clear tokens and stay on-site — call
> `msalService.instance.clearCache({ account })` then navigate in-app. The documented
> `logoutRedirect({ onRedirectNavigate: () => false })` "skip server sign-out" pattern does **not
> compile in v5** (`onRedirectNavigate` moved off the per-request type onto global
> `BrowserAuthOptions`); use `clearCache({ account })` instead. Trade-off: the Entra server session
> persists, so a later login can complete silently.


Back to the index: [msal-angular](msal-angular.md)
