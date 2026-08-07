# ASP.NET Core Controller Patterns

Reference for `[ApiController]` classes, CRUD actions, and `Program.cs` wiring.

## Rules

- All endpoints use explicit `[ApiController]` classes in `Controllers/`.
- Never use inline lambdas in `Program.cs`.
- Never use `MapGroup` extension methods.
- Use primary constructor injection — never a constructor body with `this.field = field` assignments.

## Controller Structure

```csharp
namespace my_api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class ItemsController(AppDbContext db) : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> GetAll() =>
        Ok(await db.Items.AsNoTracking().ToListAsync());

    [HttpGet("{id:int}")]
    public async Task<IActionResult> GetById(int id)
    {
        var item = await db.Items.FindAsync(id);
        return item is null ? NotFound() : Ok(item);
    }

    [HttpPost]
    public async Task<IActionResult> Create(Item item)
    {
        db.Items.Add(item);
        await db.SaveChangesAsync();
        return CreatedAtAction(nameof(GetById), new { id = item.Id }, item);
    }

    [HttpDelete("{id:int}")]
    public async Task<IActionResult> Delete(int id)
    {
        var item = await db.Items.FindAsync(id);
        if (item is null) return NotFound();
        db.Items.Remove(item);
        await db.SaveChangesAsync();
        return NoContent();
    }
}
```

## Return Types

| Scenario | Return |
|---|---|
| Success with body | `Ok(payload)` |
| Resource not found | `NotFound()` |
| Resource created | `CreatedAtAction(nameof(GetById), new { id }, resource)` |
| Delete success | `NoContent()` |

## Program.cs Registration

```csharp
builder.Services.AddControllers();

// ...

app.MapControllers();
```

Never call `AddControllers()` more than once. If auth is enabled, apply authorization at `MapControllers()`:

```csharp
app.MapControllers().RequireAuthorization();
```
