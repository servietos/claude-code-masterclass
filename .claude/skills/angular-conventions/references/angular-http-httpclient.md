# HttpClient, Methods and Request Options

## HttpClient - Traditional Approach

For complex scenarios or when you need Observable operators:

```typescript
import { Component, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { toSignal } from '@angular/core/rxjs-interop';

@Component({...})
export class Users {
  private http = inject(HttpClient);
  
  // Convert Observable to Signal
  users = toSignal(
    this.http.get<User[]>('/api/users'),
    { initialValue: [] }
  );
  
  // Or use Observable directly
  users$ = this.http.get<User[]>('/api/users');
}
```

### HTTP Methods

```typescript
private http = inject(HttpClient);

// GET
getUser(id: string) {
  return this.http.get<User>(`/api/users/${id}`);
}

// POST
createUser(user: CreateUserDto) {
  return this.http.post<User>('/api/users', user);
}

// PUT
updateUser(id: string, user: UpdateUserDto) {
  return this.http.put<User>(`/api/users/${id}`, user);
}

// PATCH
patchUser(id: string, changes: Partial<User>) {
  return this.http.patch<User>(`/api/users/${id}`, changes);
}

// DELETE
deleteUser(id: string) {
  return this.http.delete<void>(`/api/users/${id}`);
}
```

### Request Options

```typescript
this.http.get<User[]>('/api/users', {
  headers: {
    'Authorization': 'Bearer token',
    'Content-Type': 'application/json',
  },
  params: {
    page: '1',
    limit: '10',
    sort: 'name',
  },
  observe: 'response', // Get full HttpResponse
  responseType: 'json',
});
```

Back to the index: [angular-http](angular-http.md)
