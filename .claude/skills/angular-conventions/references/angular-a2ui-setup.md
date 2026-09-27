# A2UI Angular Client Setup

## Angular Client Setup

### Installation

```bash
npm install @a2ui/angular @a2ui/web_core
npm install marked   # required unconditionally — Text always injects MarkdownRenderer, see below
```

### app.config.ts

Register `A2UI_RENDERER_CONFIG` (via `useFactory` so `inject()` works inside the factory) and `A2uiRendererService`.

```typescript
// app.config.ts
import { ApplicationConfig, inject, Injector } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import {
  A2UI_RENDERER_CONFIG,
  A2uiRendererService,
  BasicCatalog,
  provideMarkdownRenderer,
} from '@a2ui/angular/v0_9';
import { marked } from 'marked';
import { ChatService } from './chat/chat.service';

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(),
    {
      provide: A2UI_RENDERER_CONFIG,
      useFactory: () => {
        const injector = inject(Injector);
        return {
          catalogs: [inject(BasicCatalog)],
          actionHandler: (action) =>
            injector.get(ChatService).handleAction(action),
        };
      },
    },
    provideMarkdownRenderer(
      async (md) => marked.parse(String(md ?? '')),
    ),
    A2uiRendererService,
  ],
};
```

`provideMarkdownRenderer` is required unconditionally, not just when `Text` components use `"variant": "markdown"`. `Text` injects `MarkdownRenderer` regardless of variant, so omitting the provider throws `NG0201: No provider found for MarkdownRenderer` at render time even when no markdown is used anywhere in the app. `marked` (or `@a2ui/markdown-it`, whose peer-dep range is stale against `@a2ui/web_core@0.10.x` and needs `--legacy-peer-deps` to install) is a required dependency, not an optional one.

Back to the index: [angular-a2ui](angular-a2ui.md)
