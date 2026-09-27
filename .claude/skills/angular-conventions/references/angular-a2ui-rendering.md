# Rendering And Feeding Surfaces

## Rendering Surfaces

Import `SurfaceComponent` from `@a2ui/angular/v0_9` and render with `<a2ui-v09-surface>`.

```typescript
// chat/chat-panel.ts
import {
  Component, ChangeDetectionStrategy, inject, DestroyRef,
} from '@angular/core';
import {
  A2uiRendererService,
  SurfaceComponent,
} from '@a2ui/angular/v0_9';
import type { A2uiClientAction } from '@a2ui/web_core/v0_9';
import { ChatService } from './chat.service';

@Component({
  selector: 'app-chat-panel',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [SurfaceComponent],
  template: `
    @for (id of chat.activeSurfaceIds(); track id) {
      <a2ui-v09-surface [surfaceId]="id" />
    }
  `,
})
export class ChatPanel {
  private readonly renderer = inject(A2uiRendererService);
  private readonly destroyRef = inject(DestroyRef);
  protected readonly chat = inject(ChatService);

  constructor() {
    const sub = this.renderer.surfaceGroup.onAction.subscribe(
      (action: A2uiClientAction) => this.chat.handleAction(action),
    );
    this.destroyRef.onDestroy(() => sub.unsubscribe());
  }
}
```

`renderer.surfaceGroup.onAction` is not a standard RxJS Observable with `takeUntilDestroyed` support. Unsubscribe manually via `DestroyRef.onDestroy`.

### Feeding messages to the renderer

Call `renderer.processMessages(messages)` whenever the agent responds. The renderer handles progressive rendering internally: components appear as soon as a valid `root` component is available, before all messages arrive.

```typescript
// chat/chat.service.ts
import { Injectable, inject, signal } from '@angular/core';
import { A2uiRendererService } from '@a2ui/angular/v0_9';
import type { A2uiMessage, A2uiClientAction } from '@a2ui/web_core/v0_9';

@Injectable({ providedIn: 'root' })
export class ChatService {
  private readonly renderer = inject(A2uiRendererService);

  readonly activeSurfaceIds = signal<string[]>([]);

  async sendMessage(text: string): Promise<void> {
    const response = await fetch('/api/agent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });

    const messages = await response.json() as A2uiMessage[];
    this.renderer.processMessages(messages);

    for (const msg of messages) {
      if ('createSurface' in msg) {
        const id = (msg as { createSurface: { surfaceId: string } }).createSurface.surfaceId;
        this.activeSurfaceIds.update((ids) => [...ids, id]);
      }
      if ('deleteSurface' in msg) {
        const id = (msg as { deleteSurface: { surfaceId: string } }).deleteSurface.surfaceId;
        this.activeSurfaceIds.update((ids) => ids.filter((x) => x !== id));
      }
    }
  }

  handleAction(action: A2uiClientAction): void {
    // Forward action context back to agent as a new user turn
    this.sendMessage(JSON.stringify({ action }));
  }
}
```

Back to the index: [angular-a2ui](angular-a2ui.md)
