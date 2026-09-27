# Pagination and Infinite Scroll

## Pagination

### Paginated Resource

```typescript
interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

@Component({
  template: `
    @if (usersResource.isLoading()) {
      <app-spinner />
    } @else if (usersResource.hasValue()) {
      <ul>
        @for (user of usersResource.value().data; track user.id) {
          <li>{{ user.name }}</li>
        }
      </ul>
      
      <div class="pagination">
        <button 
          (click)="prevPage()" 
          [disabled]="page() === 1"
        >Previous</button>
        
        <span>Page {{ page() }} of {{ usersResource.value().totalPages }}</span>
        
        <button 
          (click)="nextPage()" 
          [disabled]="page() >= usersResource.value().totalPages"
        >Next</button>
      </div>
    }
  `,
})
export class UsersList {
  page = signal(1);
  pageSize = signal(10);
  
  usersResource = httpResource<PaginatedResponse<User>>(() => ({
    url: '/api/users',
    params: {
      page: this.page().toString(),
      pageSize: this.pageSize().toString(),
    },
  }));
  
  nextPage() {
    this.page.update(p => p + 1);
  }
  
  prevPage() {
    this.page.update(p => Math.max(1, p - 1));
  }
}
```

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

Back to the index: [angular-http](angular-http.md)
