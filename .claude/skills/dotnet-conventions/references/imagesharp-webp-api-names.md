# ImageSharp WebP API names that actually compile

## The API names, because guessing costs a compile cycle

| What you want | The actual name |
|---|---|
| The encoder | `WebpEncoder`, in `SixLabors.ImageSharp.Formats.Webp` |
| Lossy vs lossless | `WebpFileFormatType.Lossy` / `.Lossless` |
| The encoder property | `WebpEncoder.FileFormat`, typed `WebpFileFormatType?` |
| Decode failure | `ImageFormatException` |

`WebpFileFormat` does not exist. It is the obvious guess, it reads correctly in a sentence, and it
does not compile. Verify a library's enum and property names against the assembly (F12 in the IDE,
or `dotnet build` on a one-line probe) rather than from memory: a plausible name is exactly the kind
of detail a model reconstructs confidently and wrongly.

`ImageFormatException` is the base of both `UnknownImageFormatException` (nothing recognised the
bytes) and `InvalidImageContentException` (the format was recognised and the content is corrupt), so
catching the base covers both. Do not catch `Exception` here: an `OutOfMemoryException` from a
decompression bomb is not a "pass it through" case.

Back to the index: [imagesharp-webp](imagesharp-webp.md)
