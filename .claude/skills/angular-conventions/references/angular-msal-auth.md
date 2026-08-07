# Angular MSAL Authentication — Overview

How to wire MSAL Angular with `@azure/msal-angular ^5.x` and `@azure/msal-browser ^5.x` for an Angular 22 standalone SPA talking to a protected .NET API.

---

## MSAL Browser v5 — Breaking API Changes

| What changed | Before (v4) | After (v5) |
|---|---|---|
| Account storage events | `instance.enableAccountStorageEvents()` | Remove — always enabled |
| Account added/removed events | `EventType.ACCOUNT_ADDED / REMOVED` | `EventType.LOGIN_SUCCESS / LOGOUT_SUCCESS` |
| Logout | `authService.logout()` | `authService.logoutRedirect()` or `logoutPopup()` |
| Navigate after redirect | `auth.navigateToLoginRequestUrl: true` in config | Pass to `handleRedirectObservable({ navigateToLoginRequestUrl })` |
| Popup redirect handler | `handleRedirectObservable()` anywhere | `APP_INITIALIZER` (see msal-angular.md) |
| Platform broker (Windows) | Default off | **Default on** — must set `allowPlatformBroker: false` |

### `BrowserAuthOptions` — removed properties

`navigateToLoginRequestUrl` is **no longer a valid key** in the `auth` config block. Remove it from `MSALInstanceFactory`. Pass it to `handleRedirectObservable()` if needed.

---

## MSAL Angular v5 — Breaking Changes

| What changed | Before (v4) | After (v5) |
|---|---|---|
| `MsalService.logout()` | Available | Removed — use `logoutRedirect()` / `logoutPopup()` |
| `protectedResourceMap` matching | Loose by default | **Strict by default** — use `path/*` wildcards |
| `handleRedirectObservable(hash)` | Accepts hash string | Deprecated — pass `{ hash: '...' }` options object |
| Token injection to `inject(TOKEN)` | String-based | Type-based — TypeScript errors without explicit types |

---

## Interaction Type — Critical Rule

**Never mix popup and redirect in the same app.** Pick one and use it everywhere:

| Concern | Popup | Redirect |
|---|---|---|
| `MsalGuard interactionType` | `Popup` | `Redirect` |
| `MsalInterceptor interactionType` | `Popup` | `Redirect` |
| `login()` method | `loginPopup()` | `loginRedirect()` |

**Recommended: use Redirect.** Popup flow has a cross-window session storage problem in Angular standalone — the popup loads the full Angular app, `APP_INITIALIZER` runs `handleRedirectObservable()` in the popup context, but the cached token request lives in the main window's session storage only. Result: `no_token_request_cache_error` in the popup, login hangs indefinitely.

---

## Popup Failure Mode (do not repeat)

Symptoms:

- Popup opens, user authenticates, popup stays open
- Main window stays at login screen
- Console in popup: `BrowserAuthError: no_token_request_cache_error`

Root cause: The popup window loads Angular, `APP_INITIALIZER` calls `handleRedirectObservable()`, MSAL tries to do a full redirect exchange but the original token request is in the **main window's session storage** (not the popup's). MSAL fails before sending `postMessage` back to opener.

Fix: switch to redirect flow (see `msal-angular.md`).

---

## App Registration Requirements

Before writing any code, verify the Entra app registration:

| Setting | Required value | Why |
|---|---|---|
| `api.requestedAccessTokenVersion` | `2` | Null (default) issues v1 tokens; `Microsoft.Identity.Web` validates the v2 issuer and rejects them, causing 401 |
| SPA redirect URIs | Must be under **SPA** platform (not Web) | Web platform issues auth codes incompatible with PKCE flows |
| `web.implicitGrantSettings.enableAccessTokenIssuance` | `false` | Implicit flow is obsolete; SPA platform uses auth code + PKCE |

Check with:

```bash
az ad app show --id <clientId> --query "api.requestedAccessTokenVersion" -o tsv
# Must return 2. If null, fix:
az ad app update --id <clientId> --set "api={'requestedAccessTokenVersion': 2}"
```

---

## Do NOT Enable Easy Auth Alongside MSAL Angular

**App Service Easy Auth and `Microsoft.Identity.Web` must never coexist.** Easy Auth intercepts requests at the infrastructure layer before .NET sees them. If `unauthenticatedClientAction` is not `AllowAnonymous`, it returns 401/redirect responses that override the app's own auth logic.

If Easy Auth was previously enabled on the App Service, delete and recreate the App Service — disabling it via CLI is unreliable when `configVersion: v2` is active.

---

## Environment Configuration

```typescript
// environment.ts / environment.prod.ts
export const environment = {
  apiUrl: 'https://your-api.azurewebsites.net',
  authEnabled: true,
  azure: {
    msalConfig: {
      auth: {
        clientId: '<SPA clientId>',
        authority: 'https://login.microsoftonline.com/<tenantId>/',
        redirectUri: '/',
      },
    },
    protectedScopes: ['api://<clientId>/access_as_user'],
  },
};
```

---

## MSAL Providers Factory

```typescript
// msal.auth.ts
import { APP_INITIALIZER } from '@angular/core';
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import {
  MsalInterceptorConfiguration,
  MsalGuardConfiguration,
  MsalInterceptor,
  MSAL_INSTANCE,
  MSAL_GUARD_CONFIG,
  MSAL_INTERCEPTOR_CONFIG,
  MsalService,
  MsalGuard,
  MsalBroadcastService,
} from '@azure/msal-angular';
import {
  PublicClientApplication,
  BrowserCacheLocation,
  InteractionType,
} from '@azure/msal-browser';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../environments/environment';

export function MSALInstanceFactory() {
  return new PublicClientApplication({
    auth: {
      clientId: environment.azure.msalConfig.auth.clientId,
      authority: environment.azure.msalConfig.auth.authority,
      redirectUri: environment.azure.msalConfig.auth.redirectUri,
      postLogoutRedirectUri: environment.azure.msalConfig.auth.redirectUri,
      // DO NOT add navigateToLoginRequestUrl here — removed in MSAL Browser v5
    },
    cache: { cacheLocation: BrowserCacheLocation.LocalStorage },
    system: {
      allowPlatformBroker: false, // REQUIRED on Windows — disables WAM broker
    },
  });
}

export function MSALInterceptorConfigFactory(): MsalInterceptorConfiguration {
  const protectedResourceMap = new Map<string, Array<string>>();
  protectedResourceMap.set(`${environment.apiUrl}/api/*`, environment.azure.protectedScopes);
  return {
    interactionType: InteractionType.Redirect,
    protectedResourceMap,
  };
}

export function MSALGuardConfigFactory(): MsalGuardConfiguration {
  return {
    interactionType: InteractionType.Redirect,
    authRequest: { scopes: environment.azure.protectedScopes },
    loginFailedRoute: '/login-failed',
  };
}

function msalInitializerFactory(msalService: MsalService) {
  return () => firstValueFrom(msalService.handleRedirectObservable(), { defaultValue: null });
}

export const msalServiceProviders = [
  { provide: HTTP_INTERCEPTORS, useClass: MsalInterceptor, multi: true },
  { provide: MSAL_INSTANCE, useFactory: MSALInstanceFactory },
  { provide: MSAL_GUARD_CONFIG, useFactory: MSALGuardConfigFactory },
  { provide: MSAL_INTERCEPTOR_CONFIG, useFactory: MSALInterceptorConfigFactory },
  MsalService,
  MsalGuard,
  MsalBroadcastService,
  {
    provide: APP_INITIALIZER,
    useFactory: msalInitializerFactory,
    deps: [MsalService],
    multi: true,
  },
];
```

---

## `protectedResourceMap` Key Rules

The `protectedResourceMap` key is matched as a URL prefix in v5 with strict matching enabled by default.

| Key | Result |
|---|---|
| `https://api.example.com/api/*` | Correct — attaches token to all `/api/*` requests |
| `https://api.example.com/api/` | Wrong — strict matching treats this as an exact URL, not a prefix |
| `https://api.example.com` | Wrong — too broad, attaches token to every request including static files |

The `/*` suffix is a special wildcard marker the v5 matcher recognizes. It is not shell glob expansion.

---

## `app.config.ts` Registration

```typescript
import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptorsFromDi, withFetch } from '@angular/common/http';
import { msalServiceProviders } from './auth/msal.auth';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(withInterceptorsFromDi(), withFetch()), // withInterceptorsFromDi() required for MsalInterceptor
    ...(environment.authEnabled ? msalServiceProviders : []),
  ],
};
```

`withInterceptorsFromDi()` is **required** because `MsalInterceptor` is registered via the class-based `HTTP_INTERCEPTORS` token. Without it, the interceptor is silently dropped and no bearer token is attached.

---

## 401 Triage — Client Side

A 401 from `https://localhost:5001/api/...` can come from either side. Find which:

1. Open DevTools > Network > failed request > check **Request Headers** for `Authorization: Bearer ...`.
2. If header is **MISSING**, this is a client problem. Most common cause: `protectedResourceMap` key without `/*` wildcard (v5 strict matching). Work through the steps below.
3. If header is **PRESENT**, the server rejected the token. Most common cause: `Audience` config is `api://<guid>` while app issues v2 tokens (token `aud` is bare GUID), causing `IDX10214`. Consult the .NET MSAL reference.

### Client-side 401 checklist

| Symptom | Cause | Fix |
|---|---|---|
| `Authorization` header missing | `protectedResourceMap` key does not match request URL | Add `/*` wildcard suffix to the key |
| `Authorization` header missing | `withInterceptorsFromDi()` absent from `provideHttpClient` | Add it to `app.config.ts` |
| 401 even with valid login | `requestedAccessTokenVersion` is null (v1 token) | Set to 2 on app registration |
| 401 with "You do not have permission to view this directory or page." | Easy Auth is blocking the request | Disable / remove Easy Auth from App Service |
| Token not attached to requests | `protectedResourceMap` key doesn't match `environment.apiUrl` prefix | Verify key matches exactly with `/*` suffix |
| Redirect loop on login | `redirectUri` not registered as SPA redirect URI | Add to app registration under SPA platform |
| First request 401s, subsequent succeed | HTTP call fires before MSAL settles | Gate calls behind `inProgress$` reaching `InteractionStatus.None` |
| Logout redirects to `login.microsoftonline.com` / shows "pick an account to sign out" | `logoutRedirect()` always hits the Entra end-session endpoint; with no account it adds the account-picker | For local-only sign-out use `instance.clearCache({ account })` + in-app navigate; for full sign-out pass `{ account }` to skip the picker (see Logout section) |

---

## Logout: server sign-out vs. local-only (v5)

`logoutRedirect()` always navigates the browser to the Entra end-session endpoint
(`login.microsoftonline.com/.../oauth2/v2.0/logout`), clearing the IdP session and — **if no
account is passed — showing a "pick an account to sign out" interstitial** before returning to
`postLogoutRedirectUri`. Choose the call by intent:

| Goal | Call |
|---|---|
| Full sign-out (terminate the Entra session too) | `msalService.logoutRedirect({ account })` — pass the active account to skip the account-picker |
| **Local-only** sign-out (clear tokens, stay on-site, **no** redirect to Microsoft) | `msalService.instance.clearCache({ account })` then `router.navigate(['/'])` |

```typescript
logout(): void {
  const account =
    this.msal?.instance.getActiveAccount() ?? this.msal?.instance.getAllAccounts()[0];
  if (account) {
    this.msal!.instance.clearCache({ account }); // local-only: wipes that account's tokens, zero network
  }
  this.router.navigate(['/']);
}
```

**v5 gotcha:** the documented `logoutRedirect({ onRedirectNavigate: () => false })` "skip server
sign-out" snippet does **not compile** in msal-browser v5 — `onRedirectNavigate` was removed from
the per-request `EndSessionRequest` type (it now lives only on the global `BrowserAuthOptions`).
Use `instance.clearCache(request?: ClearCacheRequest)` with `{ account }` instead (verified against
`@azure/msal-browser` 5.15). **Trade-off:** local-only logout leaves the Entra **server session
active**, so a later login can complete silently — usually the desired SPA UX; use full
`logoutRedirect({ account })` when the IdP session must end too.

---

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

Pair it with hiding the public nav links when `auth.isLoggedIn()` so the logged-in shell stays clean.

---

## See Also

- [`msal-angular.md`](msal-angular.md) — client wiring deep-dive: full provider setup, `APP_INITIALIZER`, `AuthStateService`, migration checklist, detailed 401 troubleshooting
- [`msal-angular-appreg.md`](msal-angular-appreg.md) — Entra app registration via Azure CLI: create from scratch, add redirect URIs, platform types

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

  login(): void  { this.msal?.loginRedirect({ scopes: environment.azure.protectedScopes }); }
  logout(): void { this.msal?.logoutRedirect(); }
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


## Anti-pattern: hand-rolled token interceptor → redirect loop

Do not write a custom interceptor that calls `acquireTokenRedirect` (or `loginRedirect`) on
failure. Combined with a missing/404 user-load call it produces an infinite loop: API call →
silent acquire fails → `acquireTokenRedirect` → Microsoft → back to app → user-load 404 →
clear user → guard → API call → … Use `MsalInterceptor` + `protectedResourceMap`, which only
acquires **silently** and never triggers interaction from inside the HTTP pipeline.


## Toggle-able auth (one flag, both ends)

Gate the whole thing behind a single `environment.authEnabled` flag so the app runs open during
development and flips to protected for prod:
- Frontend: spread MSAL providers only when enabled — `...(environment.authEnabled ? msalProviders : [])`; guards return `true` early when disabled.
- Backend (.NET): read `Auth:Enabled`; when **true** register `AddMicrosoftIdentityWebApi("AzureAd")` and an `AdminOnly` policy = `RequireAuthenticatedUser()`; when **false** register `AdminOnly` = `RequireAssertion(_ => true)` (allow-all) and skip `UseAuthentication`. Annotate protected controllers with `[Authorize(Policy = "AdminOnly")]` — it then enforces when enabled and is a no-op when disabled, with no per-toggle edits. Keep genuinely public endpoints (e.g. a read-only content feed another site consumes) un-annotated / `[AllowAnonymous]`.


## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| **Blank page the moment auth is enabled, no console error** | Nothing calls `ensureInitialized()` at startup, so the guard's observable never resolves | Call it once from the root component constructor and gate `<router-outlet>` on a `ready` signal |
| **Redirect loop bouncing through Microsoft** | A custom interceptor calls `acquireTokenRedirect` on failure, and/or the bootstrap hits a non-existent `/api/auth/me` (404) that clears the user | Use `MsalInterceptor` + `protectedResourceMap` (silent acquire only); read the user from `AccountInfo`, not `/me` |
| 401 even with valid login | `requestedAccessTokenVersion` is null (v1 token) | Set to 2 on app registration |
| 401 with `"You do not have permission to view this directory or page."` | Easy Auth is blocking the request | Disable / remove Easy Auth from App Service |
| Token not attached to requests | `protectedResourceMap` key doesn't match request URL (most often a missing `*` wildcard under strictMatching) | Verify key ends with `/api/*` and matches `environment.apiUrl` exactly |
| `redirect_uri` mismatch (AADSTS50011) | `redirectUri: '/'` resolves to `origin + '/'` (trailing slash) but the registration has no trailing slash (or vice-versa) | Make `environment.msal.redirectUri` an explicit absolute URL that matches the registered SPA redirect URI exactly |
| Redirect loop on login | `redirectUri` not registered as SPA redirect URI | Add to app registration under SPA platform |
| Stuck on `/?state=...` after login | Login started from the same URL as `redirectUri` with `navigateToLoginRequestUrl` defaulting to `true` | Pass `{ navigateToLoginRequestUrl: false }` to `handleRedirectObservable()` and let the app handle post-login navigation |
| Logout redirects to `login.microsoftonline.com` / shows "pick an account to sign out" | `logoutRedirect()` always hits the Entra end-session endpoint; with no account it adds the account-picker | For local-only sign-out use `instance.clearCache({ account })` + in-app navigate; for full sign-out pass `{ account }` to skip the picker (see Logout section) |

## Debug Auth Mode

`environment.development.ts` sets `authEnabled: false` to disable MSAL entirely during local development. The mechanic relies on three pieces working together:

| File | Role |
|---|---|
| `src/app/auth/auth.tokens.ts` | Declares `AUTH_ENABLED` injection token backed by `environment.authEnabled` |
| `src/app/auth/auth.service.ts` | `init()` checks `AUTH_ENABLED`; when false, calls `store.setUser({ email: 'claude@debug.local', isAdmin: true })` |
| `app.html` | Gates `<app-bottom-nav>` and `<app-scan-wizard>` on `@if (store.isAuthenticated())` |

`store.isAuthenticated()` is a computed signal that returns `user() !== null`. When `authEnabled` is false and `init()` seeds the debug user, the signal is true and the full shell renders. When auth is disabled WITHOUT seeding a user, `store.isAuthenticated()` stays false and the entire app shell (bottom bar, scan wizard, admin features) is hidden.

The `/login` route redirects to `/` when auth is off. The guard and MSAL interceptor are bypassed.

**Rule:** never set `authEnabled: false` without verifying that `auth.service.ts init()` seeds a fallback user. Prod `environment.ts` stays `authEnabled: true` and must not be changed.

