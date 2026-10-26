# The WebpConverter reference implementation

## The converter

```csharp
using SkiaSharp;

public static class WebpConverter
{
    public static (byte[] Bytes, string FileName, string ContentType) Convert(
        byte[] bytes, string fileName, string contentType)
    {
        if (!IsConvertible(fileName, contentType)) return (bytes, fileName, contentType);

        using var codec = SKCodec.Create(SKData.CreateCopy(bytes));
        if (codec is null) return (bytes, fileName, contentType);

        using var bitmap = SKBitmap.Decode(codec);
        if (bitmap is null) return (bytes, fileName, contentType);

        var lossy = Encode(bitmap, 82);
        var lossless = Encode(bitmap, 100);
        var best = lossless.Length < lossy.Length ? lossless : lossy;

        if (best.Length >= bytes.Length) return (bytes, fileName, contentType);

        return (best, Path.ChangeExtension(fileName, ".webp"), "image/webp");
    }

    private static byte[] Encode(SKBitmap bitmap, int quality)
    {
        using var data = bitmap.Encode(SKEncodedImageFormat.Webp, quality);
        return data.ToArray();
    }

    private static readonly HashSet<string> ConvertibleTypes =
        new(StringComparer.OrdinalIgnoreCase) { "image/jpeg", "image/jpg", "image/png" };

    private static bool IsConvertible(string fileName, string? contentType)
    {
        if (contentType is not null && ConvertibleTypes.Contains(contentType)) return true;
        return Path.GetExtension(fileName).ToLowerInvariant() is ".jpg" or ".jpeg" or ".png";
    }
}
```

Quality 100 selects lossless WebP; quality 82 is lossy. Decode goes through `SKCodec.Create` because
`SKBitmap.Decode(byte[])` throws on bytes it cannot read ([api-names](imagesharp-webp-api-names.md)).

Back to the index: [imagesharp-webp](imagesharp-webp.md)
