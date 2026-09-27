# A2UI Action Handling

## Action Handling

### How actions flow

1. Agent includes `"action": { "event": { "name": "...", "context": { ... } } }` on a Button or other interactive component.
2. User triggers the component.
3. Renderer resolves `context` path bindings from the local data model.
4. `renderer.surfaceGroup.onAction` emits an `A2uiClientAction`.
5. Your handler receives it and forwards to the agent (or handles locally).

### A2uiClientAction shape

```typescript
interface A2uiClientAction {
  name:              string;       // stable identifier set by the agent
  surfaceId:         string;
  sourceComponentId: string;
  timestamp:         string;       // ISO 8601
  context:           Record<string, unknown>;  // resolved from data-model paths
}
```

### Forwarding actions back to the agent

```typescript
handleAction(action: A2uiClientAction): void {
  // The agent receives action.name and action.context
  // and responds with new A2UI messages
  this.sendMessage(JSON.stringify({ action }));
}
```

### Optimistic local updates

Update the local data model immediately before the agent round-trip:

```typescript
handleAction(action: A2uiClientAction): void {
  if (action.name === 'increaseMiles') {
    const passenger = action.context['passenger'] as Passenger;
    this.renderer.processMessages([
      {
        version: 'v0.9',
        updateDataModel: {
          surfaceId: action.surfaceId,
          path: '/passenger',
          value: { ...passenger, bonusMiles: passenger.bonusMiles + 300 },
        },
      },
    ]);
  }
  this.sendMessage(JSON.stringify({ action }));
}
```

### functionCall actions (renderer-local)

Some actions never reach the agent. The renderer evaluates them from catalog-registered functions:

```json
{
  "id": "external-link",
  "component": "Button",
  "child": "link-label",
  "action": {
    "functionCall": {
      "call": "openUrl",
      "args": { "url": "https://example.com" }
    }
  }
}
```

Back to the index: [angular-a2ui](angular-a2ui.md)
