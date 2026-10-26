# Converting an uploaded image to WebP server-side (SkiaSharp)

Converting an uploaded JPEG or PNG to WebP inside the request, safely, with SkiaSharp.

ImageSharp is retired: 4.x requires a commercial licence key at build time and 3.1.12 carries open
advisories. Code that still loads `SixLabors.ImageSharp` is ported to SkiaSharp, never bumped to 4.x.

**A converter that can grow the file is a bug.**

| You want to... | Read |
|---|---|
| Is this the right tool for a per-request upload conversion, which packages do I add, and where do the converted bytes go next? | [scope](imagesharp-webp-scope.md) |
| I need the actual code: the SkiaSharp converter that turns an uploaded byte[] into WebP and returns bytes, name and content type. | [converter](imagesharp-webp-converter.md) |
| Lossy or lossless, why encode twice, why did optimizing 20 images take 15 minutes, and why can the output be bigger than the input? | [encode-both-or-once](imagesharp-webp-encode-both-or-once.md) |
| Building a backfill over the converter: base64 columns, sharing one implementation with the API, and which safety flags not to add. | [backfill-reuse](imagesharp-webp-backfill-reuse.md) |
| Porting ImageSharp code: what are the SkiaSharp names for lossy, lossless, resize and JPEG, and why does `SKBitmap.Decode` throw on a non-image? | [api-names](imagesharp-webp-api-names.md) |
| A PDF came back renamed .webp, or a valid PNG was skipped: what must pass through unchanged and how content-type detection works. | [passthrough](imagesharp-webp-passthrough.md) |
| How do I test the converter without committing binary fixtures, and how do I assert the result really is a WebP file? | [testing](imagesharp-webp-testing.md) |
