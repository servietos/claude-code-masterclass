# Preloading Strategies

## Preloading Strategies

### Built-in Strategies

```typescript
import { 
  provideRouter, 
  withPreloading,
  PreloadAllModules,
  NoPreloading 
} from '@angular/router';

// Preload all lazy modules
provideRouter(routes, withPreloading(PreloadAllModules))

// No preloading (default)
provideRouter(routes, withPreloading(NoPreloading))
```

### Custom Preloading Strategy

```typescript
// selective-preload.strategy.ts
@Injectable({ providedIn: 'root' })
export class SelectivePreloadStrategy implements PreloadingStrategy {
  preload(route: Route, load: () => Observable<any>): Observable<any> {
    // Only preload routes marked with data.preload = true
    if (route.data?.['preload']) {
      return load();
    }
    return of(null);
  }
}

// Routes
{
  path: 'dashboard',
  loadComponent: () => import('./dashboard.component'),
  data: { preload: true }, // Will be preloaded
}

// Config
provideRouter(routes, withPreloading(SelectivePreloadStrategy))
```

### Network-Aware Preloading

```typescript
@Injectable({ providedIn: 'root' })
export class NetworkAwarePreloadStrategy implements PreloadingStrategy {
  preload(route: Route, load: () => Observable<any>): Observable<any> {
    // Check network conditions
    const connection = (navigator as any).connection;
    
    if (connection) {
      // Don't preload on slow connections
      if (connection.saveData || connection.effectiveType === '2g') {
        return of(null);
      }
    }
    
    // Preload if marked
    if (route.data?.['preload']) {
      return load();
    }
    
    return of(null);
  }
}
```

Back to the index: [angular-routing](angular-routing.md)
