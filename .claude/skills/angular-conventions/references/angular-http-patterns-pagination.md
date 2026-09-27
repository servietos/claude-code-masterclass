# Angular HTTP: Paginated Resource

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

Back to the index: [angular-http-patterns](angular-http-patterns.md)
