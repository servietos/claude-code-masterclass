# ASP.NET Core Controller Patterns

Reference for `[ApiController]` classes, CRUD actions, and `Program.cs` wiring.

## Rules

- All endpoints use explicit `[ApiController]` classes in `Controllers/`.
- Never use inline lambdas in `Program.cs`.
- Never use `MapGroup` extension methods.
- Use primary constructor injection — never a constructor body with `this.field = field` assignments.
- **A field added to a full-replace update request is nulled by every caller that predates it.** An `Update<X>Request` record copied field by field into the entity sets an omitted optional field to null, so the first existing UI PUT after the change wipes it (it came up twice in one week: a list description, then a scene's `ReviewNote` and a video's `PitchPath`). Put "every PUT must carry the current value" into the shared contract with the client, make the field required in the client's request type so its compiler finds every caller, and test clearing to null explicitly.

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

## Route shape: the identifier is `id`, and the order is `action/{id}`

Two rules, and they are separate. A path identifier is the row's `id`, never a slug, a name or any
other natural key; and where an action has both a verb and an identifier, the literal comes first.

```csharp
[HttpGet("{id:guid}")]              // the resource itself
[HttpGet("tree/{id:guid}")]         // not {id}/tree
[HttpPut("values/{id:guid}")]       // not {id}/values
[HttpPost("import/{id:guid}")]      // not {id}/import
[HttpGet("export/{id:guid}")]       // not {id}/export
[HttpGet("repos")]                  // a collection needs no identifier
```

A slug still belongs on the resource (`RepoDto` carries both `RepoId` and `Slug`, and a human-facing
SPA route may well be `/config/:slug`), but it is resolved to an id client-side and the API only
ever sees the id. Response DTOs follow: a payload that echoed `Slug` back now echoes `RepoId`, which
is what makes a caller still passing a slug a compile error rather than a silent 404.

**A field is never a path segment.** Renaming a resource or changing one of its fields is
`PUT api/items/{id}` with the field in the body, not `PUT api/items/{id}/display-name`. A literal
segment names a sub-resource or an action with its own lifecycle (`runs`, `schedule`, `export`),
never a column. The same holds for the SPA: `/items/:id`, never `/items/:name`. A repo that already
fixes the order of sub-resource segments keeps its order; this rule is only about what may be one.

**A free-text key in a route segment breaks on its first slash.** `DELETE api/models/deepinfra/MiniMaxAI%2FMiniMax-M2.5`
returns 404 against `[HttpDelete("{provider}/{modelName}")]` while the row exists: the encoded
slash never binds to one segment, so every model whose name carries a `/` (most DeepInfra and IONOS
ids) can be neither updated nor deleted, and the client reads the 404 as "no longer exists". Address
the row by its id (`[HttpDelete("{modelId:guid}")]`); where the table has no id yet, add one in a
delta rather than escaping the name. Prove it from the network log plus the database row before
touching data.

**Order the literal-prefixed routes above the bare `{id}` route in the file**, and constrain the
bare one (`{id:guid}`, `{id:int}`). Without the constraint, `GET api/config/export/…` is ambiguous
with a resource whose id is literally "export"; with it, the constraint settles it, and file order
keeps the intent readable.

**The neighbouring action is the weakest evidence there is for a route's shape.** A controller that
violates the convention violates it on every action, so copying the sibling reproduces the bug with
perfect local consistency, and the diff looks like it belongs. Before adding an endpoint, survey the
whole repo rather than the file:

```bash
grep -rn '\[Http[A-Za-z]*("' --include=*.cs | grep -oE '\[Http[A-Za-z]+\("[^"]*"\)' | sort | uniq -c | sort -rn
```

The majority shape is the convention. Where the file in hand disagrees with it, say so and ask
rather than propagating either: this exact case shipped `GET api/config/{slug}/export` into a review
and needed every layer reworked, because eight sibling actions all had it wrong and the twelve
correct examples were in other controllers.

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

## A public address is derived, never stored, and resolves on the id

A `Link` column holding `/knowledge-catalogue/{slug}/` is a rename waiting to break: the slug moves, the
column does not, and nothing errors. Two rules remove the whole class of bug.

**Derive the address on read** from the immutable key plus the current slug, and stop reading the
stored column:

```csharp
private static string ItemLink(int id, string slug) => $"/knowledge-catalogue/{id}-{slug}/";
```

Apply it on *every* read path in the same pass: the list projection, the detail, the sibling refs
and the admin DTO. One projection left on `Link = i.Link` is a surface that disagrees with the rest,
and it will be the one nobody looks at. EF cannot always translate the interpolation inside a
`.Select()`, so project the id and slug and fill the link after materialization.

**Resolve on the leading id and ignore the rest of the key**, so every address ever minted for that
row keeps working and a rename needs no redirect:

```csharp
var dash = key.IndexOf('-');
var head = dash < 0 ? key : key[..dash];

var published = db.Items.Where(i => i.IsPublished);
var item = int.TryParse(head, out var id)
    ? await published.FirstOrDefaultAsync(i => i.Id == id)
    : await published.FirstOrDefaultAsync(i => i.Slug == key);   // pre-scheme addresses
```

Build the branch as two `FirstOrDefaultAsync` calls over a shared query rather than one predicate
with a captured bool ternary, which EF may refuse to translate.

**The test that asserted the stored value will now fail, and that failure is the feature.** Fix it
by computing the expectation from the response (`$"/knowledge-catalogue/{fetched.Id}-{slug}/"`) while
leaving the request payload sending the old literal, so the test proves the API returns something
different from what was sent. Rewriting the expectation to whatever the code now returns turns a
real assertion into an echo.

Leaving the write path (`item.Link = req.Link`) in place makes the column write-only. That is a
deliberate, temporary state at best: either drop the field from the save request and the admin form,
or say plainly that it is ignored.

## An upsert keyed on a mutable field cannot serve a rename

A create endpoint that upserts by a natural key is fine as a create endpoint:

```csharp
var repo = await db.Repos.FirstOrDefaultAsync(r => r.Name == name, cancellationToken);
if (repo is null) { repo = new Repo { RepoId = Guid.CreateVersion7(), Name = name }; db.Repos.Add(repo); }
repo.Name = name;
```

Reusing it for an edit that can change `Name` silently inserts a second row instead of updating the
first, because a changed name matches nothing. The insert is not an error anywhere: the POST returns
201, a frontend store that upserts on the primary key correctly appends a genuinely new id, and the
only visible symptom is a duplicate in whatever list renders the collection.

**Before wiring an edit to an existing write endpoint, read that endpoint's lookup key.** When the
key is a field the edit can change, that endpoint cannot serve the edit however well its name reads.
Add an address-by-id sibling and leave the create path alone:

```csharp
[HttpPut("{repoId:guid}")]
public async Task<IActionResult> Update(Guid repoId, UpdateRepoRequest request, CancellationToken cancellationToken = default)
{
    try
    {
        var repo = await repository.UpdateRepoAsync(repoId, request, cancellationToken);
        return repo is null ? NotFound() : Ok(repo);
    }
    catch (ArgumentException ex)
    {
        return BadRequest(ex.Message);
    }
}
```

The repository method looks the row up by id, and checks the new name against a *different* id
before saving, so the uniqueness the create path relied on survives:

```csharp
var taken = await db.Repos.AnyAsync(r => r.Name == name && r.RepoId != repoId, cancellationToken);
if (taken) throw new ArgumentException("A repository with this name already exists.");
```

A frontend spec that asserts only "the service method was called with the new value" passes against
the broken version. Assert that the collection did not grow.

## An aggregate endpoint must not fail whole

An endpoint that composes independent sections into one DTO gives every dependency a veto over all of
them. `GetAllAsync` below builds seven sections eagerly; `AiModels` fetches over HTTP from a service
that was not deployed yet, and it is built *before* `FeatureFlags`:

```csharp
public async Task<SettingsDto> GetAllAsync() => new SettingsDto
{
    Ai = GetAi(),
    AiModels = await GetAiModelsAsync(),
    FeatureFlags = await GetFeatureFlagsAsync(),
    Integration = GetIntegrationInfo(),
};
```

One unreachable host 500s the whole payload, so the settings page rendered as if nothing were
configured and every feature flag read `false`. The section that failed was unrelated to the one the
user was looking at, which is what makes this expensive to diagnose: the symptom names the innocent
section.

Rules:

- A section whose source can be unreachable is served from a **persisted local copy**, refreshed in
  the background, never fetched inline on the read path. In-process caching does not satisfy this: a
  cold container must answer without the dependency.
- Where a live fetch is genuinely required, catch that section's own exception and return it degraded
  (empty list plus a status field), so the sibling sections still reach the client.
- Order is not a fix. Building the risky section last still fails the request; it only changes which
  sections were computed before the throw.
- Config that names a host is a claim about DNS, not a fact. `SecretsMcp:BaseUrl` pointed at a
  hostname that had never existed. Resolve the host from inside the container (`getent hosts <host>`)
  before reading the exception as an app bug.
- The client half of the rule: a swallowed error must render as an error. The Angular store logged
  the 500 to the console and left the model `{}`, so the page showed its "nothing configured" empty
  state. An empty state is reachable only from a successful response.
