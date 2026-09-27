# The WebpConverter reference implementation

## The converter

```csharp
using SixLabors.ImageSharp;
using SixLabors.ImageSharp.Formats.Webp;

public static class WebpConverter
{
    public static (byte[] Bytes, string FileName, string ContentType) Convert(
        byte[] bytes, string fileName, string contentType)
    {
        if (!IsConvertible(fileName, contentType)) return (bytes, fileName, contentType);

        try
        {
            using var image = Image.Load(bytes);

            var lossy = Encode(image, new WebpEncoder { FileFormat = WebpFileFormatType.Lossy, Quality = 82 });
            var lossless = Encode(image, new WebpEncoder { FileFormat = WebpFileFormatType.Lossless });
            var best = lossless.Length < lossy.Length ? lossless : lossy;

            if (best.Length >= bytes.Length) return (bytes, fileName, contentType);

            return (best, Path.ChangeExtension(fileName, ".webp"), "image/webp");
        }
        catch (ImageFormatException)
        {
            return (bytes, fileName, contentType);
        }
    }

    private static byte[] Encode(Image image, WebpEncoder encoder)
    {
        using var ms = new MemoryStream();
        image.Save(ms, encoder);
        return ms.ToArray();
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

Back to the index: [imagesharp-webp](imagesharp-webp.md)
