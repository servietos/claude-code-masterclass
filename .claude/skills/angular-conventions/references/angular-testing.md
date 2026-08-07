# Angular Testing with Vitest

Unit test Angular components, services, and signals using Vitest and Angular's TestBed.

## File Structure

Create `.spec.ts` files adjacent to source files. Use `describe`/`it` blocks with names that describe behavior, not implementation.

```
user-list.component.ts
user-list.component.spec.ts
user.service.ts
user.service.spec.ts
```

## Component Testing

Test signal inputs, outputs, and user interactions. Mock services via `TestBed.configureTestingModule`.

```typescript
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { UserListComponent } from './user-list.component';
import { UserService } from './user.service';
import { describe, it, expect, beforeEach } from 'vitest';
import { of } from 'rxjs';

describe('UserListComponent', () => {
  let component: UserListComponent;
  let fixture: ComponentFixture<UserListComponent>;
  let userService: { getUsers: ReturnType<typeof vi.fn> };

  beforeEach(async () => {
    userService = { getUsers: vi.fn().mockReturnValue(of([])) };

    await TestBed.configureTestingModule({
      imports: [UserListComponent],
      providers: [{ provide: UserService, useValue: userService }],
    }).compileComponents();

    fixture = TestBed.createComponent(UserListComponent);
    component = fixture.componentInstance;
  });

  it('renders users when input is provided', () => {
    const users = [{ id: 1, name: 'Alice' }];
    fixture.componentRef.setInput('users', users);
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Alice');
  });

  it('emits selected user on card click', () => {
    const user = { id: 1, name: 'Alice' };
    fixture.componentRef.setInput('users', [user]);
    fixture.detectChanges();

    const emitted: unknown[] = [];
    component.selected.subscribe((v) => emitted.push(v));

    fixture.nativeElement.querySelector('app-user-card').click();
    expect(emitted).toEqual([user]);
  });
});
```

## Service Testing

Mock HTTP with `HttpTestingController`. Always call `httpMock.verify()` in `afterEach`.

```typescript
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { UserService } from './user.service';
import { describe, it, expect, beforeEach, afterEach } from 'vitest';

describe('UserService', () => {
  let service: UserService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [UserService, provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(UserService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('fetches users from API', () => {
    const mockUsers = [{ id: 1, name: 'Alice' }];
    service.getUsers().subscribe((users) => expect(users).toEqual(mockUsers));

    httpMock.expectOne('/api/users').flush(mockUsers);
  });

  it('handles API errors', () => {
    service.getUsers().subscribe({ error: (e) => expect(e.status).toBe(500) });
    httpMock.expectOne('/api/users').flush('error', { status: 500, statusText: 'Server Error' });
  });
});
```

## Signal Testing

Test computed values and effects directly — no TestBed needed.

```typescript
import { signal, computed } from '@angular/core';
import { describe, it, expect } from 'vitest';

describe('signal computation', () => {
  it('updates computed value when source changes', () => {
    const count = signal(0);
    const doubled = computed(() => count() * 2);

    expect(doubled()).toBe(0);
    count.set(5);
    expect(doubled()).toBe(10);
  });
});
```

## Async Testing

Use `fakeAsync` + `tick` for synchronous time control. Use the `done` callback for observable-based assertions.

```typescript
import { fakeAsync, tick } from '@angular/core/testing';

it('loads data after delay', fakeAsync(() => {
  component.load();
  tick(200);
  expect(component.data()).toBeDefined();
}));

it('subscribes to observable', (done) => {
  service.getData().subscribe((v) => {
    expect(v).toBeTruthy();
    done();
  });
});
```

## Mocking Strategy

Mock external dependencies (services, HTTP). Test in isolation. Verify calls with spies.

```typescript
// Mock the service, not internal implementation
const mockService = { getUsers: vi.fn().mockReturnValue(of([{ id: 1, name: 'Test' }])) };

// Never test private methods
// expect(component['privateMethod']).toHaveBeenCalled(); // wrong
```

## Coverage Goals

Target 80%+ coverage. Prioritize:

1. Happy path scenarios
2. Error handling and edge cases
3. User interactions and emitted outputs
4. Service integration points
5. State transitions

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


## Component Testing — `provideRouter` for `routerLink` Templates

`TestBed.createComponent` instantiates the component's template directives. A template using `routerLink`/`routerLinkActive` will fail with `NG0201: No provider found for ActivatedRoute` unless the router is provided. Add `provideRouter([])`:

```typescript
import { provideRouter } from '@angular/router';

TestBed.configureTestingModule({
  providers: [
    provideRouter([]),
    { provide: SomeStore, useValue: storeMock },
  ],
});
```

For pure logic checks (method delegation, signal wiring), you can read `createComponent(X).componentInstance` directly without `detectChanges()` — the constructor and field initializers still run.

