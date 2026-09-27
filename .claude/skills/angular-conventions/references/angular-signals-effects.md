# Effects, Untracked Reads and Debug Logging

### effect() - Side Effects

```typescript
import { signal, effect, inject, DestroyRef } from '@angular/core';

@Component({...})
export class Search {
  query = signal('');
  
  constructor() {
    // Effect runs when query changes
    effect(() => {
      console.log('Search query:', this.query());
    });
    
    // Effect with cleanup
    effect((onCleanup) => {
      const timer = setInterval(() => {
        console.log('Current query:', this.query());
      }, 1000);
      
      onCleanup(() => clearInterval(timer));
    });
  }
}
```

**Effect rules:**
- Run in injection context (constructor or with `runInInjectionContext`)
- Automatically cleaned up when component destroys

## Untracked Reads

```typescript
import { untracked } from '@angular/core';

const a = signal(1);
const b = signal(2);

// Only depends on 'a', not 'b'
const result = computed(() => {
  const aVal = a();
  const bVal = untracked(() => b());
  return aVal + bVal;
});
```

## Signal Debugging

```typescript
// Debug effect to log signal changes
effect(() => {
  console.log('State changed:', {
    count: this.count(),
    items: this.items(),
    filter: this.filter(),
  });
});

// Conditional debugging
const DEBUG = signal(false);

effect(() => {
  if (untracked(() => DEBUG())) {
    console.log('Debug:', this.state());
  }
});
```

Back to the index: [angular-signals](angular-signals.md)
