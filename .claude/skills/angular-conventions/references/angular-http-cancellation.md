# Request Cancellation and Debounced Search

## Request Cancellation

### With resource()

```typescript
// resource() automatically handles cancellation via abortSignal
searchResource = resource({
  params: () => ({ q: this.query() }),
  loader: async ({ params, abortSignal }) => {
    const response = await fetch(`/api/search?q=${params.q}`, {
      signal: abortSignal, // Cancels if params change
    });
    return response.json();
  },
});
```

### With HttpClient

```typescript
@Component({...})
export class Search implements OnDestroy {
  private http = inject(HttpClient);
  private destroyRef = inject(DestroyRef);
  
  query = signal('');
  results = signal<Result[]>([]);
  
  private searchSubscription?: Subscription;
  
  search() {
    // Cancel previous request
    this.searchSubscription?.unsubscribe();
    
    this.searchSubscription = this.http
      .get<Result[]>(`/api/search?q=${this.query()}`)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(results => this.results.set(results));
  }
}
```

### Debounced Search

```typescript
@Component({...})
export class SearchDebounced {
  query = signal('');
  
  private http = inject(HttpClient);
  
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
}
```

Back to the index: [angular-http](angular-http.md)
