# Signal and async specs

## Signal Testing

Test computed values and effects directly, no TestBed needed.

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
Back to the index: [angular-testing](angular-testing.md)
