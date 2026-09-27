# Converting an uploaded image to WebP server-side (ImageSharp)

Converting an uploaded JPEG or PNG to WebP inside the request, safely, with ImageSharp.

**A converter that can grow the file is a bug.**

| You want to... | Read |
|---|---|
| Is this the right tool for a per-request upload conversion, what package do I add, and where do the converted bytes go next? | [scope](imagesharp-webp-scope.md) |
| I need the actual code: the ImageSharp converter that turns an uploaded byte[] into WebP and returns bytes, name and content type. | [converter](imagesharp-webp-converter.md) |
| Lossy or lossless, why encode twice, why did optimizing 20 images take 15 minutes, and why can the output be bigger than the input? | [encode-both-or-once](imagesharp-webp-encode-both-or-once.md) |
| Building a backfill over the converter: base64 columns, sharing one implementation with the API, and which safety flags not to add. | [backfill-reuse](imagesharp-webp-backfill-reuse.md) |
| Does WebpFileFormat exist, what is the encoder property called, and which exception does a failed decode throw? | [api-names](imagesharp-webp-api-names.md) |
| A PDF came back renamed .webp, or a valid PNG was skipped: what must pass through unchanged and how content-type detection works. | [passthrough](imagesharp-webp-passthrough.md) |
| How do I test the converter without committing binary fixtures, and how do I assert the result really is a WebP file? | [testing](imagesharp-webp-testing.md) |
