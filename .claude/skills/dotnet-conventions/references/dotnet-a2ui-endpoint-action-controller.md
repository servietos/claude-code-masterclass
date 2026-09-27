# A2UI Query and Action Controller

### Controller

```csharp
[ApiController]
[Route("api/a2ui")]
public class A2UiController(A2UiAgentService agent) : ControllerBase
{
    [HttpPost("query")]
    public async Task<IActionResult> Query(
        [FromBody] A2UiQueryRequest request, CancellationToken ct)
    {
        var messages = await agent.QueryAsync(request.Query, ct);
        return Ok(messages);
    }

    [HttpPost("action")]
    public async Task<IActionResult> HandleAction(
        [FromBody] A2UiActionMessage action, CancellationToken ct)
    {
        var query = MapActionToQuery(action.Action);
        var messages = await agent.QueryAsync(query, ct);
        return Ok(messages);
    }

    private static string MapActionToQuery(A2UiActionPayload action) =>
        action.Name switch
        {
            "submit_booking" => FormatBookingQuery(action.Context),
            "confirm_order"  => FormatConfirmQuery(action.Context),
            "cancel"         => "Reset the surface and return to the initial view.",
            _                => $"The user triggered the '{action.Name}' action. Continue the conversation."
        };

    private static string FormatBookingQuery(JsonElement ctx)
    {
        var date  = ctx.TryGetProperty("date",      out var d) ? d.GetString()    : "unspecified";
        var size  = ctx.TryGetProperty("partySize", out var p) ? p.GetRawText()   : "unspecified";
        return $"Confirm a reservation for {size} people on {date}.";
    }

    private static string FormatConfirmQuery(JsonElement ctx)
    {
        var id = ctx.TryGetProperty("orderId", out var o) ? o.GetString() : "unspecified";
        return $"Show the confirmation screen for order {id}.";
    }
}

public record A2UiQueryRequest(
    [property: JsonPropertyName("query")] string Query);
```

Keep `MapActionToQuery` purely declarative: each arm produces a natural-language query and nothing else. The LLM owns domain reasoning. Never embed DB calls, conditional state, or business rules in switch arms.

Back to the index: [dotnet-a2ui-endpoint](dotnet-a2ui-endpoint.md)
