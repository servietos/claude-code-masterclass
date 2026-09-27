# resource() for Generic Async Data

## resource() - Generic Async Data

For non-HTTP async operations or custom fetch logic:

```typescript
import { resource, signal } from '@angular/core';

@Component({...})
export class Search {
  query = signal('');
  
  searchResource = resource({
    // Reactive params - triggers reload when changed
    params: () => ({ q: this.query() }),
    
    // Async loader function
    loader: async ({ params, abortSignal }) => {
      if (!params.q) return [];
      
      const response = await fetch(`/api/search?q=${params.q}`, {
        signal: abortSignal,
      });
      return response.json() as Promise<SearchResult[]>;
    },
  });
}
```

### Resource with Default Value

```typescript
todosResource = resource({
  defaultValue: [] as Todo[],
  params: () => ({ filter: this.filter() }),
  loader: async ({ params }) => {
    const res = await fetch(`/api/todos?filter=${params.filter}`);
    return res.json();
  },
});

// value() returns Todo[] (never undefined)
```

### Conditional Loading

```typescript
const userId = signal<string | null>(null);

userResource = resource({
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

Back to the index: [angular-http](angular-http.md)
