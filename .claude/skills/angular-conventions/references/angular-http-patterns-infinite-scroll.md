# Angular HTTP: Infinite Scroll

Accumulate pages into one growing list instead of replacing the page at a time.

### Infinite Scroll

```typescript
@Component({
  template: `
    <ul>
      @for (user of allUsers(); track user.id) {
        <li>{{ user.name }}</li>
      }
    </ul>
    
    @if (isLoading()) {
      <app-spinner />
    }
    
    @if (hasMore()) {
      <button (click)="loadMore()">Load More</button>
    }
  `,
})
export class InfiniteUsers {
  private http = inject(HttpClient);
  
  private page = signal(1);
  private users = signal<User[]>([]);
  private totalPages = signal(1);
  
  allUsers = this.users.asReadonly();
  isLoading = signal(false);
  hasMore = computed(() => this.page() < this.totalPages());
  
  constructor() {
    this.loadPage(1);
  }
  
  loadMore() {
    this.loadPage(this.page() + 1);
  }
  
  private async loadPage(page: number) {
    this.isLoading.set(true);
    
    try {
      const response = await firstValueFrom(
        this.http.get<PaginatedResponse<User>>('/api/users', {
          params: { page: page.toString(), pageSize: '20' },
        })
      );
      
      this.users.update(users => [...users, ...response.data]);
      this.page.set(page);
      this.totalPages.set(response.totalPages);
    } finally {
      this.isLoading.set(false);
    }
  }
}
```

Back to the index: [angular-http-patterns](angular-http-patterns.md)
