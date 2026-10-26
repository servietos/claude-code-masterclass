# An in-app chat reuses the MCP tools by reflection, read-only by default

An app that hosts an MCP server and also has its own AI chat tends to grow a second, hand-written
tool list for the chat: a prompt section naming a few tools and a `switch` dispatching them. Every
tool added to the MCP server afterwards silently misses the chat. In the bico planner the chat knew
5 of 64 tools when the user asked "are all mcp methods used in the chat"; the new absence tools were
among the missing.

## Procedure

1. **Classify every tool once, on the attribute.** Mark tools that never write to the database, never
   send mail and never start a run with `[McpServerTool(ReadOnly = true)]`; mark deleting tools
   `Destructive = true`. Decide from the method body, not from the description text. The properties
   exist in `ModelContextProtocol` 2.1.0. MCP clients see the same hints, so the work is not chat-only.
2. **Build the chat catalogue by reflection** over the `[McpServerToolType]` classes, taking only
   `ReadOnly = true` methods: the snake_case name the MCP server exposes, the method's and each
   parameter's `[Description]`, parameter names, types and defaults. Generate the prompt's tool
   section from it; never type tool names into the prompt.
3. **Dispatch through DI:** resolve the tool class from the request's `IServiceProvider` (tool
   classes take constructor dependencies) and bind JSON args by parameter name and type, applying
   defaults for optional ones. Parse args leniently: models send numbers and booleans unquoted.
4. **Refuse everything else at dispatch.** A write or unknown tool name returns
   `{"error":"Tool '<name>' is not available in chat."}` and is never invoked, even if the model
   names it.
5. **Opt out per tool when the payload does not fit a chat**, e.g. a base64 PDF, with a small marker
   attribute (`[ChatExcluded]`) rather than by dropping `ReadOnly`, which other clients rely on.
6. **Keep the prompt bounded:** first description sentence per tool (about 260 chars) and short
   parameter descriptions (about 90 chars).

## Prove it

- A test asserts the catalogue equals exactly the set of `ReadOnly = true` methods minus opt-outs,
  and that its names match the MCP server's own names.
- A test requests a write tool and asserts the error and that the database is unchanged.
- Live: ask the chat a question only a newly added read tool can answer ("wer ist am 15.10.
  abwesend" answered from `get_employee_absences`).
