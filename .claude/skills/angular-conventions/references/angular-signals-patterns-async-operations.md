# Angular Signals: debounced search and optimistic updates

## Async Operations

### Debounced Search

```typescript
@Component({...})
export class Search {
  query = signal('');
  
  private http = inject(HttpClient);
  
  // Debounced search using toObservable
  results = toSignal(
    toObservable(this.query).pipe(
      debounceTime(300),
      distinctUntilChanged(),
      filter(q => q.length >= 2),
      switchMap(q => this.http.get<Result[]>(`/api/search?q=${q}`)),
      catchError(() => of([]))
    ),
    { initialValue: [] }
  );
  
  // Loading state
  private searching = signal(false);
  readonly isSearching = this.searching.asReadonly();

  constructor() {
    // Track loading state
    effect(() => {
      const q = this.query();
      if (q.length >= 2) {
        this.searching.set(true);
      }
    });

    effect(() => {
      this.results(); // Subscribe to results
      this.searching.set(false);
    });
  }
}
```

### Optimistic Updates

```typescript
@Injectable({ providedIn: 'root' })
export class Todo {
  private todos = signal<Todo[]>([]);
  readonly items = this.todos.asReadonly();
  
  private http = inject(HttpClient);
  
  async toggleTodo(id: string): Promise<void> {
    // Optimistic update
    const previousTodos = this.todos();
    this.todos.update(todos =>
      todos.map(t => t.id === id ? { ...t, done: !t.done } : t)
    );
    
    try {
      await firstValueFrom(
        this.http.patch(`/api/todos/${id}/toggle`, {})
      );
    } catch {
      // Rollback on error
      this.todos.set(previousTodos);
    }
  }
}
```

Back to the index: [angular-signals-patterns](angular-signals-patterns.md)
