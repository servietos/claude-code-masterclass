# A2UI Message Shapes

## Message Shape

All messages are JSON objects with a `"version"` key and exactly one operation key. In streaming mode the agent emits JSONL (newline-delimited JSON); in non-streaming mode a JSON array is returned. The client processes each object independently.

### createSurface

Initializes a rendering container. Always send first.

```json
{
  "version": "v0.9",
  "createSurface": {
    "surfaceId": "passenger-card",
    "catalogId": "https://a2ui.org/specification/v0_9/catalogs/basic/catalog.json",
    "sendDataModel": true
  }
}
```

`sendDataModel: true` instructs the renderer to attach the full local data model to every outgoing action message, enabling stateless agents that never track client state themselves.

### updateComponents

Provides a flat adjacency list of components. The renderer builds the tree at render time from ID references.

```json
{
  "version": "v0.9",
  "updateComponents": {
    "surfaceId": "passenger-card",
    "components": [
      { "id": "root",       "component": "Card",   "child": "content" },
      { "id": "content",    "component": "Column",  "children": ["headline", "name-row", "btn"] },
      { "id": "headline",   "component": "Text",    "text": "Passenger", "variant": "h2" },
      { "id": "name-row",   "component": "Row",     "children": ["first-name", "last-name"] },
      {
        "id": "first-name",
        "component": "Text",
        "text": { "path": "/passenger/firstName" },
        "variant": "body"
      },
      {
        "id": "last-name",
        "component": "Text",
        "text": { "path": "/passenger/lastName" },
        "variant": "body"
      },
      {
        "id": "btn",
        "component": "Button",
        "child": "btn-label",
        "action": {
          "event": {
            "name": "increaseMiles",
            "context": { "passenger": { "path": "/passenger" } }
          }
        }
      },
      { "id": "btn-label",  "component": "Text",    "text": "Add Miles", "variant": "body" }
    ]
  }
}
```

Key rules for the component list:

- Every list must contain a component with `"id": "root"`, that is the tree entry point.
- `"child"` (string) holds one child ID; `"children"` (string array) holds an ordered list.
- Literal values are inline strings: `"text": "Hello"`.
- Data-bound values are path objects: `"text": { "path": "/passenger/firstName" }`. Absolute paths (leading `/`) resolve from the data model root. Relative paths resolve within the nearest collection scope during list iteration.
- Function calls embed as: `{ "call": "formatNumber", "args": { "value": { "path": "/count" }, "decimals": 0 }, "returnType": "string" }`.

### updateDataModel

Seeds or patches the surface data model. Bound components re-render automatically. Can arrive before, after, or interleaved with `updateComponents`.

```json
{
  "version": "v0.9",
  "updateDataModel": {
    "surfaceId": "passenger-card",
    "path": "/passenger",
    "value": {
      "id": 42,
      "firstName": "Anna",
      "lastName": "Miller",
      "bonusMiles": 1200
    }
  }
}
```

Send granular patches (only the changed path) rather than replacing the entire model on every turn.

### deleteSurface

Removes a surface and all associated component and data-model state.

```json
{
  "version": "v0.9",
  "deleteSurface": { "surfaceId": "passenger-card" }
}
```

Back to the index: [angular-a2ui](angular-a2ui.md)
