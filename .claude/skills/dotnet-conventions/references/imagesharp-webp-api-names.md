# SkiaSharp names that actually compile, and the ImageSharp calls they replace

Probed on SkiaSharp 4.153.1 on 2026-10-24 with a pixel-for-pixel round trip; verify again on a
different major (F12 in the IDE, or a one-file console probe) rather than from memory.

| What you want | SkiaSharp | Replaces (ImageSharp) |
|---|---|---|
| Decode, null for a non-image | `SKCodec.Create(SKData.CreateCopy(bytes))`, then `SKBitmap.Decode(codec)` | `Image.Load`, catch `ImageFormatException` |
| Lossy WebP | `bitmap.Encode(SKEncodedImageFormat.Webp, 82)` | `WebpEncoder { FileFormat = WebpFileFormatType.Lossy, Quality = 82 }` |
| Lossless WebP | `bitmap.Encode(SKEncodedImageFormat.Webp, 100)`, or explicitly `bitmap.PeekPixels().Encode(new SKWebpEncoderOptions(SKWebpEncoderCompression.Lossless, 75))` | `WebpFileFormatType.Lossless` |
| JPEG | `bitmap.Encode(SKEncodedImageFormat.Jpeg, quality)` | `SaveAsJpeg(new JpegEncoder { Quality = q })` |
| Resize | `bitmap.Resize(new SKImageInfo(w, h), new SKSamplingOptions(SKCubicResampler.Mitchell))` | `Mutate(x => x.Resize(...))` |
| Centre-crop to a square | `bitmap.ExtractSubset(dest, SKRectI.Create(x, y, side, side))`, then resize | `ResizeMode.Crop`, `AnchorPositionMode.Center` |
| Width and height | `bitmap.Width`, `bitmap.Height` (or `codec.Info` before decoding) | `image.Width`, `image.Height` |

**`SKBitmap.Decode(byte[])` throws `ArgumentNullException` on bytes it cannot read.** It does not
return null, so a port that swaps `catch (ImageFormatException)` for a null check turns every
uploaded PDF into a 500. `SKCodec.Create` returns null for the same bytes; gate on it.

**Quality 100 is lossless.** `SKEncodedImageFormat.Webp` at 100 round-trips pixel for pixel and
produced the same bytes as the explicit `SKWebpEncoderCompression.Lossless` call. With the explicit
options, the quality argument is effort, not fidelity: higher is slower and smaller.

`SKWebpEncoderOptions`, `SKWebpEncoderCompression` and `SKEncodedImageFormat` live in the `SkiaSharp`
namespace; there is no separate formats namespace.

Back to the index: [imagesharp-webp](imagesharp-webp.md)
