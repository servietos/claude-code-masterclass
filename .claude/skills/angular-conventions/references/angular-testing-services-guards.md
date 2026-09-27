# Service and functional guard specs

## Service Testing

The `provideHttpClient()` + `provideHttpClientTesting()` setup and the request/flush examples live in
[`angular-http`](angular-http.md) under "Testing HTTP". Two rules that section does not state:

- Call `httpMock.verify()` in `afterEach` of **every** HTTP spec, not just the first one.
- Match requests that carry query parameters with the predicate overload, never a bare path string.
  Both the failure it produces and the fix are in [`angular-test-doubles`](angular-test-doubles.md).

## Functional Guard / Resolver Testing

Functional guards (`CanActivateFn`, `CanMatchFn`) call `inject()`, so run them inside `TestBed.runInInjectionContext`. Mock `MsalService` via its `instance` shape and `Router` via `parseUrl`, then assert the boolean or the returned `UrlTree`.

```typescript
import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { MsalService } from '@azure/msal-angular';
import { describe, it, expect, afterEach, vi } from 'vitest';
import { canMatchAuth } from './msal-auth.guard';

function configure(activeAccount: unknown, accounts: unknown[]) {
  const msalMock = { instance: { getActiveAccount: () => activeAccount, getAllAccounts: () => accounts } };
  const urlTree = { redirectTo: '/' };
  const routerMock = { parseUrl: vi.fn(() => urlTree) };
  TestBed.configureTestingModule({
    providers: [
      { provide: MsalService, useValue: msalMock },
      { provide: Router, useValue: routerMock },
    ],
  });
  return { routerMock, urlTree };
}

const run = () => TestBed.runInInjectionContext(() => canMatchAuth({} as never, [] as never));

describe('canMatchAuth', () => {
  afterEach(() => TestBed.resetTestingModule());

  it('allows access when an account exists', () => {
    configure({ username: 'a@b.at' }, []);
    expect(run()).toBe(true);
  });

  it('redirects a logged-out user to /', () => {
    const { routerMock, urlTree } = configure(null, []);
    expect(run()).toBe(urlTree);
    expect(routerMock.parseUrl).toHaveBeenCalledWith('/');
  });
});
```

If the guard reads `isAuthEnabled()` (which checks `environment.authEnabled` and a `localStorage` flag), set/clear that `localStorage` key per-test in `afterEach` to exercise both the enabled and disabled branches.

Back to the index: [angular-testing](angular-testing.md)
