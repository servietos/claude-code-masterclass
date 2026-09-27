# Upload and download endpoints for a SQL-stored file

## Upload endpoint: multipart, buffered, size-capped

```csharp
[HttpPost("{id:guid}/file")]
[RequestSizeLimit(10 * 1024 * 1024)]
public async Task<IActionResult> UploadFile(Guid id, IFormFile file, [FromForm] string? caption)
{
    using var buffer = new MemoryStream();
    await file.CopyToAsync(buffer);
    await service.SaveFileAsync(id, buffer.ToArray(), file.FileName, file.ContentType, caption);
    return NoContent();
}
```

- `IFormFile` plus `[FromForm]` scalars makes the endpoint `multipart/form-data` only. It cannot
  also accept a JSON body, so a client that was posting JSON has to change, and any `.http` file or
  test modelling the request has to send parts rather than a body.
- `[RequestSizeLimit]` is explicit and per-endpoint. Relying on the host default means the cap moves
  when the hosting does, and a reverse proxy in front of it has its own limit that must agree.
- Buffer to `byte[]` rather than handing the request stream to EF: the stream is not seekable and is
  gone by the time `SaveChangesAsync` runs.
- To shrink an uploaded image before it is stored, convert here: [`imagesharp-webp`](imagesharp-webp.md).

## Download endpoint: return a `FileResult`

```csharp
[HttpGet("{id:guid}/file")]
public async Task<IActionResult> GetFile(Guid id)
{
    var file = await service.GetFileAsync(id);
    return file is null ? NotFound() : File(file.Content, file.ContentType, file.FileName);
}
```

`File(bytes, contentType, fileName)` is what produces a correct `Content-Disposition`. Writing the
bytes to the response by hand, or returning the entity as JSON and decoding base64 in the client,
both lose the filename and the type the browser needs in order to save the file with the right
extension.

Back to the index: [sql-stored-files](sql-stored-files.md)
