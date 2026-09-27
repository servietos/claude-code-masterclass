# Testing the converter and proving the output is WebP

## Testing without committing binary fixtures

Generate the input in the test with ImageSharp itself. A repo that accumulates `.png` fixtures for
image tests gets one per case and reviews none of them.

```csharp
private static byte[] PngOf(int w, int h, Color fill)
{
    using var image = new Image<Rgba32>(w, h);
    image.Mutate(ctx => ctx.Fill(fill));
    using var ms = new MemoryStream();
    image.SaveAsPng(ms);
    return ms.ToArray();
}
```

Cover the four outcomes: a PNG converts, a PDF's bytes come back identical, garbage bytes come back
identical, and a file whose WebP would be larger comes back identical.

## Proof it still holds

A WebP file is a RIFF container: bytes 0..3 are `RIFF` and bytes 8..11 are `WEBP`. Assert that on the
converter's output rather than trusting the returned content type, and assert it again on a file
pulled back out of storage:

```csharp
Encoding.ASCII.GetString(result.Bytes, 0, 4).Should().Be("RIFF");
Encoding.ASCII.GetString(result.Bytes, 8, 4).Should().Be("WEBP");
result.Bytes.Length.Should().BeLessThan(original.Length);
```

On the wire, `file downloaded.webp` reporting `RIFF (little-endian) data, Web/P image` is the same
check from outside the process.

Back to the index: [imagesharp-webp](imagesharp-webp.md)
