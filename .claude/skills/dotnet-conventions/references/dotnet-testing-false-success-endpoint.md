# Endpoints That Report Success for Nothing

## An endpoint that reports success for work it did not do

A handler shaped `if (entity != null) { ...mutate... } return Ok(new Result { Success = true });`
reports success when the lookup matched nothing. The caller cannot distinguish "applied" from "I
found nothing and gave up", and every layer above inherits the lie — in one codebase this shape
existed on four write endpoints at once, including the delete that every test teardown called, which
is why fixtures accumulated for weeks while cleanup reported success.

Return an explicit refusal instead, reusing the result type the endpoint already returns for its
other rejections rather than inventing a second shape:

```csharp
var es = await dc.EmployeeSchedules.FirstOrDefaultAsync(s => s.ID == param.ID);
if (es == null)
{
    return Ok(new MoveAssignmentResult
    {
        Success = false,
        Reason = param.ID == Guid.Empty ? "Kein Termin übergeben." : "Termin nicht gefunden."
    });
}
```

Distinguish "the caller sent nothing" (`Guid.Empty`, an unbound or absent body) from "a real id that
matched no row" — they have different causes and different fixes. Cover both with tests asserting
the reason **and** that nothing was written. And when auditing, check the siblings: this shape
travels in families, because the handlers were written by copying each other.

Back to the index: [dotnet-testing](dotnet-testing.md)
