# What A2UI Is, And When To Reach For It

A2UI is an open protocol for AI agents to emit declarative JSON that an Angular client renders as native UI components, with no arbitrary code execution and no unsafe string evaluation.

## What is A2UI

A2UI separates UI _intent_ (agent JSON) from UI _rendering_ (Angular client). The agent describes which catalog components to show and how to bind them to data. The client renders only components that exist in its pre-approved catalog, making generative UI safe across trust boundaries.

The protocol is stateless on the agent side: agents output a stream of JSON messages; the client owns the local data model and the live DOM. Input fields update the local model immediately; the network round-trip happens only when the user triggers an action.

**Protocol status (as of June 2026):** v0.9.1 is stable/production. v1.0 is release candidate (adds `actionResponse`, action IDs, `surfaceProperties`). Import from `@a2ui/angular/v0_9` until v1.0 is declared stable.

## When to Use / When Not to Use

**Use A2UI when:**

- An AI agent must present data in a structured, interactive UI at runtime (variable form fields, dynamic layouts).
- The exact UI shape is not known at build time.
- You want the same agent to drive multiple render targets (Angular, Flutter, React) without changing agent code.
- You need to compose many small data-driven surfaces inside a chat-like conversation.

**Do not use A2UI when:**

- The UI is fully known at build time, build a regular Angular component.
- The agent only produces text or markdown, use an async pipe with a markdown renderer.
- You need pixel-perfect custom layouts with complex animations, custom catalogs help but complex designs belong in dedicated components.

Back to the index: [angular-a2ui](angular-a2ui.md)
