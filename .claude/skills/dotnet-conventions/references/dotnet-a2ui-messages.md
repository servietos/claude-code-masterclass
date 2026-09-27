# A2UI Message Types and Validation

When to use: you are defining or validating the C# types that cross the A2UI wire.
Setup and wiring live in [`dotnet-a2ui`](dotnet-a2ui.md); the endpoint itself in
[`dotnet-a2ui-endpoint`](dotnet-a2ui-endpoint.md); SSE in [`dotnet-a2ui-streaming`](dotnet-a2ui-streaming.md).

| You want to... | Read |
|---|---|
| Define the server-to-client v0.9 envelope and its payload records | [envelope](dotnet-a2ui-messages-envelope.md) |
| Know the shape of one `updateComponents.components` entry | [component-nodes](dotnet-a2ui-messages-component-nodes.md) |
| Build Column, Row, Card, Text, Button, TextField, DateTimeInput nodes in C# | [component-factory](dotnet-a2ui-messages-component-factory.md) |
| Express a literal, a data-model path or an interpolated string | [bindings](dotnet-a2ui-messages-bindings.md) |
| Deserialize the action event the Angular client POSTs back | [action](dotnet-a2ui-messages-action.md) |
| Validate generated JSON against the catalog schema | [validation](dotnet-a2ui-messages-validation.md) |

Two rules that hold wherever you enter:

- Exactly one component per message must carry `"id": "root"` to anchor the tree
- Paths starting with `/` resolve from the data model root. Paths without a leading `/` resolve relative to the current collection item (inside templated `children`).
