# Querying and upserting the blob without materialising it

## The bytes are never selected into a DTO

The DTO carries the metadata and nothing else, so a list of a thousand rows costs a few kilobytes:

```csharp
public record ItemDto(Guid Id, string Name, string? FileName, string? ContentType, int? FileSize);

var rows = await db.Items.AsNoTracking()
    .Select(i => new ItemDto(
        i.Id,
        i.Name,
        db.ItemFiles.Where(f => f.ItemId == i.Id).Select(f => f.FileName).FirstOrDefault(),
        db.ItemFiles.Where(f => f.ItemId == i.Id).Select(f => f.ContentType).FirstOrDefault(),
        db.ItemFiles.Where(f => f.ItemId == i.Id).Select(f => (int?)f.FileSize).FirstOrDefault()))
    .ToListAsync();
```

Those subqueries translate to one `LEFT JOIN`. With no navigation property this is the only shape
available, which is the point: the projection lists the columns it wants and `Content` is not one of
them. The single-row read that does want the bytes is its own method, called by one endpoint:

```csharp
public Task<ItemFile?> GetFileAsync(Guid itemId) =>
    db.ItemFiles.AsNoTracking().FirstOrDefaultAsync(f => f.ItemId == itemId);
```

The write side is an upsert, because the key is the owner's id and a second upload for the same item
is a replacement, not a new row. `Add` on an existing key throws at `SaveChangesAsync`:

```csharp
public async Task SaveFileAsync(Guid itemId, byte[] content, string fileName, string contentType)
{
    var file = await db.ItemFiles.FirstOrDefaultAsync(f => f.ItemId == itemId);
    if (file is null)
    {
        file = new ItemFile { ItemId = itemId };
        db.ItemFiles.Add(file);
    }

    file.Content = content;
    file.FileName = fileName;
    file.ContentType = contentType;
    file.FileSize = content.Length;
    await db.SaveChangesAsync();
}
```

The lookup is tracked, so no `AsNoTracking()` here, and it does load the old bytes in order to
overwrite them. Where that matters, `ExecuteUpdateAsync` replaces the columns without materialising
the entity.

Back to the index: [sql-stored-files](sql-stored-files.md)
