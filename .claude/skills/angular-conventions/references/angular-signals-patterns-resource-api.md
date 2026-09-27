# Angular Signals: the resource() API

## Resource API

The `resource()` API handles async data fetching with signals:

```typescript
import { resource, signal, computed } from '@angular/core';

@Component({...})
export class UserProfile {
  userId = signal<string>('');
  
  // Resource fetches data when params change
  userResource = resource({
    params: () => ({ id: this.userId() }),
    loader: async ({ params, abortSignal }) => {
      const response = await fetch(`/api/users/${params.id}`, {
        signal: abortSignal,
      });
      return response.json() as Promise<User>;
    },
  });
  
  // Access resource state
  user = computed(() => this.userResource.value());
  isLoading = computed(() => this.userResource.isLoading());
  error = computed(() => this.userResource.error());
}
```

### Resource Status

```typescript
const userResource = resource({...});

// Status signals
userResource.value();      // Current value or undefined
userResource.hasValue();   // Boolean - has resolved value
userResource.error();      // Error or undefined
userResource.isLoading();  // Boolean - currently loading
userResource.status();     // 'idle' | 'loading' | 'reloading' | 'resolved' | 'error' | 'local'

// Manual reload
userResource.reload();

// Local updates
userResource.set(newValue);
userResource.update(current => ({ ...current, name: 'Updated' }));
```

### Resource with Default Value

```typescript
const todosResource = resource({
  defaultValue: [] as Todo[],
  params: () => ({ filter: this.filter() }),
  loader: async ({ params }) => {
    const response = await fetch(`/api/todos?filter=${params.filter}`);
    return response.json();
  },
});

// value() returns Todo[] (never undefined due to defaultValue)
```

### Conditional Loading

```typescript
const userId = signal<string | null>(null);

const userResource = resource({
  params: () => {
    const id = userId();
    // Return undefined to skip loading
    return id ? { id } : undefined;
  },
  loader: async ({ params }) => {
    return fetch(`/api/users/${params.id}`).then(r => r.json());
  },
});
// Status is 'idle' when params returns undefined
```

Back to the index: [angular-signals-patterns](angular-signals-patterns.md)
