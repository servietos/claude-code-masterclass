# HTTP Error Handling and Bad Response Bodies

## Error Handling

### With httpResource

```typescript
@Component({
  template: `
    @if (userResource.error(); as error) {
      <div class="error">
        <p>{{ getErrorMessage(error) }}</p>
        <button (click)="userResource.reload()">Retry</button>
      </div>
    }
  `,
})
export class UserCmpt {
  userResource = httpResource<User>(() => `/api/users/${this.userId()}`);
  
  getErrorMessage(error: unknown): string {
    if (error instanceof HttpErrorResponse) {
      return error.error?.message || `Error ${error.status}: ${error.statusText}`;
    }
    return 'An unexpected error occurred';
  }
}
```

### With HttpClient

```typescript
import { catchError, retry } from 'rxjs';

getUser(id: string) {
  return this.http.get<User>(`/api/users/${id}`).pipe(
    retry(2), // Retry up to 2 times
    catchError((error: HttpErrorResponse) => {
      console.error('Error fetching user:', error);
      return throwError(() => new Error('Failed to load user'));
    })
  );
}
```

## Guard Array Responses Before Storing

TypeScript HTTP types are wishes, not guarantees. The actual JSON can arrive as `null` (CORS or SSL failures, API quirks) even when the declared type is `T[]`. Angular's native `@for` then throws `TypeError: newCollection[Symbol.iterator] is not a function` at runtime on the next change detection, and the bug stays silent until that response lands.

When storing array responses in an NgRx SignalStore via `tapResponse` (or any `patchState` of a list signal), wrap with `Array.isArray`:

```typescript
next: (items) => patchState(store, { items: Array.isArray(items) ? items : [] })
```

Apply the same guard to nested arrays inside response objects, for example `detail.Entries`, `detail.Quotas`.

Back to the index: [angular-http](angular-http.md)
