# BasicCatalog And Custom Catalogs

## Catalogs

### BasicCatalog

`BasicCatalog` provides 15+ general-purpose components. Register it with `inject(BasicCatalog)`, it is an Angular injectable class.

| Category | Components |
|---|---|
| Layout | `Row`, `Column`, `Card`, `Tabs` |
| Content | `Text`, `Image`, `Icon`, `Divider` |
| Input | `Button`, `TextField`, `CheckBox`, `Slider`, `DateTimeInput` |

> **Verify:** The official client-setup guide also exports a `minimalCatalog` object constant (used without `inject()`). Check which export is present in the installed package version; `inject(BasicCatalog)` is preferred in Angular 22 for DI consistency.

### Custom Catalog

Extend `BasicCatalogBase` when you need domain-specific components. The catalog is an Angular injectable, so it participates in the DI graph.

```typescript
// catalog/custom-catalog.ts
import { Injectable, inject } from '@angular/core';
import { BasicCatalogBase } from '@a2ui/angular/v0_9';
import { BASIC_FUNCTIONS } from '@a2ui/web_core/v0_9';  // verify export name
import { chartEntry } from './chart/chart';

@Injectable({ providedIn: 'root' })
export class CustomCatalog extends BasicCatalogBase {
  constructor() {
    super({
      // URI is the catalogId agents must reference in createSurface.catalogId
      id: 'https://yourapp.example.com/catalogs/v1/catalog.json',
      extraComponents: [chartEntry],
      functions: [...BASIC_FUNCTIONS],
    });
  }
}
```

Register in `app.config.ts`:

```typescript
{
  provide: A2UI_RENDERER_CONFIG,
  useFactory: () => ({
    catalogs: [inject(CustomCatalog)],
    actionHandler: (action) => inject(ChatService).handleAction(action),
  }),
},
```

Back to the index: [angular-a2ui](angular-a2ui.md)
