# httpResource() and Rendering Its Status

## httpResource() - Signal-Based HTTP

`httpResource()` wraps HttpClient with signal-based state management:

```typescript
import { Component, signal } from '@angular/core';
import { httpResource } from '@angular/common/http';

interface User {
  id: number;
  name: string;
  email: string;
}

@Component({
  selector: 'app-user-profile',
  template: `
    @if (userResource.isLoading()) {
      <p>Loading...</p>
    } @else if (userResource.error()) {
      <p>Error: {{ userResource.error()?.message }}</p>
      <button (click)="userResource.reload()">Retry</button>
    } @else if (userResource.hasValue()) {
      <h1>{{ userResource.value().name }}</h1>
      <p>{{ userResource.value().email }}</p>
    }
  `,
})
export class UserProfile {
  userId = signal('123');
  
  // Reactive HTTP resource - refetches when userId changes
  userResource = httpResource<User>(() => `/api/users/${this.userId()}`);
}
```

### httpResource Options

```typescript
// Simple GET request
userResource = httpResource<User>(() => `/api/users/${this.userId()}`);

// With full request options
userResource = httpResource<User>(() => ({
  url: `/api/users/${this.userId()}`,
  method: 'GET',
  headers: { 'Authorization': `Bearer ${this.token()}` },
  params: { include: 'profile' },
}));

// With default value
usersResource = httpResource<User[]>(() => '/api/users', {
  defaultValue: [],
});

// Skip request when params undefined
userResource = httpResource<User>(() => {
  const id = this.userId();
  return id ? `/api/users/${id}` : undefined;
});
```

### Resource State

```typescript
// Status signals
userResource.value()      // Current value or undefined
userResource.hasValue()   // Boolean - has resolved value
userResource.error()      // Error or undefined
userResource.isLoading()  // Boolean - currently loading
userResource.status()     // 'idle' | 'loading' | 'reloading' | 'resolved' | 'error' | 'local'

// Actions
userResource.reload()     // Manually trigger reload
userResource.set(value)   // Set local value
userResource.update(fn)   // Update local value
```

## Loading States Pattern

```typescript
@Component({
  template: `
    @switch (dataResource.status()) {
      @case ('idle') {
        <p>Enter a search term</p>
      }
      @case ('loading') {
        <app-spinner />
      }
      @case ('reloading') {
        <app-data [data]="dataResource.value()" />
        <app-spinner size="small" />
      }
      @case ('resolved') {
        <app-data [data]="dataResource.value()" />
      }
      @case ('error') {
        <app-error 
          [error]="dataResource.error()" 
          (retry)="dataResource.reload()" 
        />
      }
    }
  `,
})
export class Data {
  query = signal('');
  dataResource = httpResource<Data[]>(() => 
    this.query() ? `/api/search?q=${this.query()}` : undefined
  );
}
```

Back to the index: [angular-http](angular-http.md)
