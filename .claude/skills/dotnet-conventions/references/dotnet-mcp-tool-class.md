# Writing an MCP tool class

## Tool Class Structure

```csharp
using System.ComponentModel;
using ModelContextProtocol.Server;

[McpServerToolType]
internal class MyTools
{
    private readonly IMyService _service;
    private readonly ILogger<MyTools> _logger;

    public MyTools(IMyService service, ILogger<MyTools> logger)
    {
        _service = service;
        _logger = logger;
    }

    [McpServerTool]
    [Description("Short description of what this tool does")]
    public async Task<string> DoSomething(
        [Description("What this parameter controls")] string input,
        [Description("Optional flag with a default")] bool flag = false)
    {
        var result = await _service.ProcessAsync(input, flag);
        return result;
    }
}
```

- One `[McpServerToolType]` per class; one `[McpServerTool]` per method.
- Every parameter must have a `[Description("...")]` attribute — MCP clients use this for introspection.
- Return `string` for simple text results; return a typed DTO for structured data.
- Optional parameters use default values (`= false`, `= 8`, etc.).
- Nullable parameters (`string?`) accept absent values from the MCP client.
- All tools should be `async Task<T>` unless computation is truly synchronous.

## Errors the client must be able to read

The SDK (verified on `ModelContextProtocol` 2.2.0) turns any exception a tool throws into
`An error occurred invoking '<tool>'.` and keeps the real message only when the exception is an
`McpException`. A provider 402 ("prepayment credits are depleted") thrown as a plain `Exception`
reaches the client as that generic line, and the cause is visible only in the server log.

1. Derive every exception a tool lets escape with a user-actionable message from `McpException`
   (`public sealed class ProviderRequestException(int? status, string message) : McpException(message)`).
   That is more than HTTP failures: a 200 response with no payload ("Gemini response contained no
   image part"), a polling timeout, and every input check (missing first frame, unknown media id,
   duplicate model) are actionable too. Use a second type for input errors
   (`ToolInputException(string message) : McpException(message)`) and convert repository
   `ArgumentException` validation at the tool boundary. Grep the services for
   `throw new InvalidOperationException` and `throw new ArgumentException` after the first fix: the
   first live pass converted only the HTTP path and the "no image part" case stayed generic.
   A call-tool filter cannot do this centrally: the SDK catches tool exceptions before filters run.
   Genuine bugs (`NullReferenceException`) stay generic on purpose.
2. Put the upstream status and body in the message: `"Gemini image API returned 402: ..."`.
3. Never swallow a failure into an empty result (`catch { }` returning `{}`): return a note that names
   the cause, for example a `Notes` list on the result DTO.

Prove it with an in-memory client and server over pipes that calls the tool and asserts the error
text contains the upstream status; on a plain `Exception` base the test sees only the generic line.
Proven in media-creator-mcp, 2026-10-08 (`ProviderErrorTests`).

Back to the index: [dotnet-mcp](dotnet-mcp.md)
