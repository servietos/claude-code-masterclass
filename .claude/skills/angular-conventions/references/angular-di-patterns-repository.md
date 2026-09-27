# Repository Pattern

### Repository Pattern

```typescript
// Generic repository interface
export abstract class Repository<T extends { id: string }> {
  abstract getAll(): Promise<T[]>;
  abstract getById(id: string): Promise<T | null>;
  abstract create(item: Omit<T, 'id'>): Promise<T>;
  abstract update(id: string, item: Partial<T>): Promise<T>;
  abstract delete(id: string): Promise<void>;
}

// HTTP implementation
@Injectable()
export class HttpUserRepo extends Repository<User> {
  private http = inject(HttpClient);
  private apiUrl = inject(API_URL);
  
  async getAll(): Promise<User[]> {
    return firstValueFrom(this.http.get<User[]>(`${this.apiUrl}/users`));
  }
  
  async getById(id: string): Promise<User | null> {
    return firstValueFrom(
      this.http.get<User>(`${this.apiUrl}/users/${id}`).pipe(
        catchError(() => of(null))
      )
    );
  }
  
  async create(user: Omit<User, 'id'>): Promise<User> {
    return firstValueFrom(this.http.post<User>(`${this.apiUrl}/users`, user));
  }
  
  async update(id: string, user: Partial<User>): Promise<User> {
    return firstValueFrom(this.http.patch<User>(`${this.apiUrl}/users/${id}`, user));
  }
  
  async delete(id: string): Promise<void> {
    await firstValueFrom(this.http.delete(`${this.apiUrl}/users/${id}`));
  }
}

// Provide implementation
{ provide: Repository, useClass: HttpUserRepo }
```

Back to the index: [angular-di-patterns](angular-di-patterns.md)
