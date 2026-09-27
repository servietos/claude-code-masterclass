# DestroyRef and Cleanup

## DestroyRef and Cleanup

### Automatic Cleanup

```typescript
import { DestroyRef, inject } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

@Component({...})
export class Data {
  private destroyRef = inject(DestroyRef);
  private dataService = inject(DataSvc);
  
  constructor() {
    // Auto-unsubscribe when component destroys
    this.dataService.data$
      .pipe(takeUntilDestroyed())
      .subscribe(data => {
        console.log(data);
      });
  }
  
  // Or use DestroyRef directly
  ngOnInit() {
    const subscription = this.dataService.updates$.subscribe();
    
    this.destroyRef.onDestroy(() => {
      subscription.unsubscribe();
      console.log('Cleaned up!');
    });
  }
}
```

### In Services

```typescript
@Injectable()
export class WebSocket {
  private destroyRef = inject(DestroyRef);
  private socket: WebSocket | null = null;
  
  constructor() {
    this.destroyRef.onDestroy(() => {
      this.socket?.close();
    });
  }
  
  connect(url: string) {
    this.socket = new WebSocket(url);
  }
}
```

### takeUntilDestroyed Outside Constructor

```typescript
@Component({...})
export class My {
  private destroyRef = inject(DestroyRef);

  loadData() {
    // Pass destroyRef when using outside constructor
    this.http.get('/api/data')
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe();
  }
}
```

Back to the index: [angular-di](angular-di.md)
