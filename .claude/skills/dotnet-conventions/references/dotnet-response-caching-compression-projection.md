# Project away columns the response never emits

## 1. Project away what you never emit

An assembler that loads entities and reads two fields off them pulls every column, including
`nvarchar(max)` blobs. `AsNoTracking()` does not help: it changes change-tracking, not the SELECT list.

```csharp
var rows = await db.Fighters.AsNoTracking().OrderBy(f => f.SortOrder)
    .Select(f => new
    {
        f.Id,
        f.De,
        f.En,
        f.WeightClassId,
        PhotoLength = (int?)f.PhotoData!.Length
    })
    .ToListAsync();
```

**Carrying a length instead of the blob.** Where the response emits a cache-buster derived from the
blob (`?v={data.Length}`), `.Length` translates to SQL `LEN()` and is computed server-side, so the
emitted value is unchanged and the bytes never leave SQL.

**Preserve the null/empty distinction exactly.** `string?` blob columns need `(int?)x!.Length`:
NULL stays `null`, `''` yields `0`, so `length > 0` reproduces `!string.IsNullOrEmpty(x)` term for
term. Getting this wrong silently adds or drops keys for rows with an empty column.

**`LEN()` ignores trailing spaces, `String.Length` does not.** For base64 this cannot bite, but do not
reason about it: prove it with the byte diff below.

Back to the index: [dotnet-response-caching-compression](dotnet-response-caching-compression.md)
