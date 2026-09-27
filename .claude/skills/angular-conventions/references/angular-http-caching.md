# HTTP Caching Strategies

## Caching Strategies

### Simple In-Memory Cache

```typescript
@Injectable({ providedIn: 'root' })
export class CachedUser {
  private http = inject(HttpClient);
  private cache = new Map<string, { data: User; timestamp: number }>();
  private cacheDuration = 5 * 60 * 1000; // 5 minutes
  
  getUser(id: string): Observable<User> {
    const cached = this.cache.get(id);
    
    if (cached && Date.now() - cached.timestamp < this.cacheDuration) {
      return of(cached.data);
    }
    
    return this.http.get<User>(`/api/users/${id}`).pipe(
      tap(user => {
        this.cache.set(id, { data: user, timestamp: Date.now() });
      })
    );
  }
  
  invalidateCache(id?: string) {
    if (id) {
      this.cache.delete(id);
    } else {
      this.cache.clear();
    }
  }
}
```

### Signal-Based Cache

```typescript
@Injectable({ providedIn: 'root' })
export class UserCache {
  private http = inject(HttpClient);
  
  // Cache as signal
  private usersCache = signal<Map<string, User>>(new Map());
  
  // Computed for easy access
  users = computed(() => Array.from(this.usersCache().values()));
  
  getUser(id: string): User | undefined {
    return this.usersCache().get(id);
  }
  
  async fetchUser(id: string): Promise<User> {
    const cached = this.getUser(id);
    if (cached) return cached;
    
    const user = await firstValueFrom(
      this.http.get<User>(`/api/users/${id}`)
    );
    
    this.usersCache.update(cache => {
      const newCache = new Map(cache);
      newCache.set(id, user);
      return newCache;
    });
    
    return user;
  }
}
```

Back to the index: [angular-http](angular-http.md)
