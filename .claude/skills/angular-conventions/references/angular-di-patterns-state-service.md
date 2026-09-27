# State Service Pattern

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

Back to the index: [angular-di-patterns](angular-di-patterns.md)
