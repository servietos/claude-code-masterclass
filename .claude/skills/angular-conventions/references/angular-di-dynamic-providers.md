# Dynamic Providers: Feature Flags and Platform-Specific Services

## Dynamic Providers

### Feature Flags

```typescript
export const FEATURE_FLAGS = new InjectionToken<FeatureFlags>('FeatureFlags');

interface FeatureFlags {
  newDashboard: boolean;
  betaFeatures: boolean;
  experimentalApi: boolean;
}

// Load from API
{
  provide: FEATURE_FLAGS,
  useFactory: async () => {
    const response = await fetch('/api/features');
    return response.json();
  },
}

// Use in components
@Component({...})
export class Dashboard {
  private features = inject(FEATURE_FLAGS);
  
  showNewDashboard = this.features.newDashboard;
}
```

### Platform-Specific Services

```typescript
export abstract class Storage {
  abstract get(key: string): string | null;
  abstract set(key: string, value: string): void;
  abstract remove(key: string): void;
}

@Injectable()
export class BrowserStorage extends Storage {
  get(key: string) { return localStorage.getItem(key); }
  set(key: string, value: string) { localStorage.setItem(key, value); }
  remove(key: string) { localStorage.removeItem(key); }
}

@Injectable()
export class ServerStorage extends Storage {
  private store = new Map<string, string>();

  get(key: string) { return this.store.get(key) ?? null; }
  set(key: string, value: string) { this.store.set(key, value); }
  remove(key: string) { this.store.delete(key); }
}

// Provide based on platform
import { PLATFORM_ID, isPlatformBrowser } from '@angular/common';

{
  provide: Storage,
  useFactory: (platformId: object) => {
    return isPlatformBrowser(platformId)
      ? new BrowserStorage()
      : new ServerStorage();
  },
  deps: [PLATFORM_ID],
}
```

Back to the index: [angular-di](angular-di.md)
