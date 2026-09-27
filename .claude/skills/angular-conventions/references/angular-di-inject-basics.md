# Injecting with inject()

## Basic Injection

### Using inject()

Prefer `inject()` over constructor injection:

```typescript
import { Component, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { User } from './user.service';

@Component({
  selector: 'app-user-list',
  template: `...`,
})
export class UserList {
  // Inject dependencies
  private http = inject(HttpClient);
  private userService = inject(User);
  
  // Can use immediately
  users = this.userService.getUsers();
}
```

### Injectable Services

```typescript
import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root', // Singleton at root level
})
export class User {
  private http = inject(HttpClient);
  
  private users = signal<User[]>([]);
  readonly users$ = this.users.asReadonly();
  
  async loadUsers() {
    const users = await firstValueFrom(
      this.http.get<User[]>('/api/users')
    );
    this.users.set(users);
  }
}
```

Back to the index: [angular-di](angular-di.md)
