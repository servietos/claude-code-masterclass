# Component specs and spec file layout

## File Structure

Create `.spec.ts` files adjacent to source files. Use `describe`/`it` blocks with names that describe behavior, not implementation.

```
user-list.component.ts
user-list.component.spec.ts
user.service.ts
user.service.spec.ts
```

A spec is routinely named for the *concept* rather than the file: `with-tasks.feature.ts` is covered by
`with-tasks.spec.ts`. Never read a missing same-stem spec as missing coverage; see
[`angular-test-coverage`](angular-test-coverage.md).

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

Drive real events rather than calling handlers: `querySelector(...).click()` covers the template's
listener closures, `component.onSave()` does not. In a zoneless app the dispatched event is also the
only thing that repaints a plain (non-signal) field.

Back to the index: [angular-testing](angular-testing.md)
