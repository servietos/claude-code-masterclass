# Service Patterns: Facade, State Service, Repository

## Service Patterns

### Facade Service

Combine multiple services into a single API:

```typescript
@Injectable({ providedIn: 'root' })
export class ShopFacade {
  private productService = inject(Product);
  private cartService = inject(Cart);
  private orderService = inject(Order);
  
  // Expose combined state
  readonly products = this.productService.products;
  readonly cart = this.cartService.items;
  readonly cartTotal = this.cartService.total;
  
  // Unified actions
  addToCart(productId: string, quantity: number) {
    const product = this.productService.getById(productId);
    if (product) {
      this.cartService.add(product, quantity);
    }
  }
  
  async checkout() {
    const items = this.cartService.items();
    const order = await this.orderService.create(items);
    this.cartService.clear();
    return order;
  }
}
```

### State Service Pattern

```typescript
interface UserState {
  user: User | null;
  loading: boolean;
  error: string | null;
}

@Injectable({ providedIn: 'root' })
export class UserState {
  private state = signal<UserState>({
    user: null,
    loading: false,
    error: null,
  });
  
  // Selectors
  readonly user = computed(() => this.state().user);
  readonly loading = computed(() => this.state().loading);
  readonly error = computed(() => this.state().error);
  readonly isAuthenticated = computed(() => this.state().user !== null);
  
  // Actions
  setUser(user: User) {
    this.state.update(s => ({ ...s, user, loading: false, error: null }));
  }
  
  setLoading() {
    this.state.update(s => ({ ...s, loading: true, error: null }));
  }
  
  setError(error: string) {
    this.state.update(s => ({ ...s, loading: false, error }));
  }
  
  clear() {
    this.state.set({ user: null, loading: false, error: null });
  }
}
```

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

Back to the index: [angular-di](angular-di.md)
