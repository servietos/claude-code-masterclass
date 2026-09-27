# HTTP Service Layer Pattern

## Service Layer Pattern

Encapsulate HTTP logic in services:

```typescript
import { Injectable, inject, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { httpResource } from '@angular/common/http';

export interface User {
  id: string;
  name: string;
  email: string;
}

@Injectable({ providedIn: 'root' })
export class User {
  private http = inject(HttpClient);
  private baseUrl = '/api/users';
  
  // Current user ID for reactive fetching
  private currentUserId = signal<string | null>(null);
  
  // Reactive resource that updates when currentUserId changes
  currentUser = httpResource<User>(() => {
    const id = this.currentUserId();
    return id ? `${this.baseUrl}/${id}` : undefined;
  });
  
  // Set current user to fetch
  selectUser(id: string) {
    this.currentUserId.set(id);
  }
  
  // CRUD operations
  getAll() {
    return this.http.get<User[]>(this.baseUrl);
  }
  
  getById(id: string) {
    return this.http.get<User>(`${this.baseUrl}/${id}`);
  }
  
  create(user: Omit<User, 'id'>) {
    return this.http.post<User>(this.baseUrl, user);
  }
  
  update(id: string, user: Partial<User>) {
    return this.http.patch<User>(`${this.baseUrl}/${id}`, user);
  }
  
  delete(id: string) {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }
}
```

Back to the index: [angular-http](angular-http.md)
