# Signal and Observable Interop

## RxJS Interop

### toSignal() - Observable to Signal

```typescript
import { toSignal } from '@angular/core/rxjs-interop';
import { interval } from 'rxjs';

@Component({...})
export class Timer {
  private http = inject(HttpClient);
  
  // From observable - requires initial value or allowUndefined
  counter = toSignal(interval(1000), { initialValue: 0 });
  
  // From HTTP - undefined until loaded
  users = toSignal(this.http.get<User[]>('/api/users'));
  
  // With requireSync for synchronous observables (BehaviorSubject)
  private user$ = new BehaviorSubject<User | null>(null);
  currentUser = toSignal(this.user$, { requireSync: true });
}
```

### toObservable() - Signal to Observable

```typescript
import { toObservable } from '@angular/core/rxjs-interop';
import { switchMap, debounceTime } from 'rxjs';

@Component({...})
export class Search {
  query = signal('');
  
  private http = inject(HttpClient);
  
  // Convert signal to observable for RxJS operators
  results = toSignal(
    toObservable(this.query).pipe(
      debounceTime(300),
      switchMap(q => this.http.get<Result[]>(`/api/search?q=${q}`))
    ),
    { initialValue: [] }
  );
}
```

Back to the index: [angular-signals](angular-signals.md)
