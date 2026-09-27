# What must pass through the converter untouched

## What must pass through untouched

- **Anything that is not JPEG or PNG.** Same bytes, same name, same content type. A PDF that comes
  back renamed `.webp` is a data-loss bug that only surfaces at download time.
- **Anything that fails to decode.** Callers upload broken files; the endpoint's job is to store what
  it was given, not to reject it on the converter's behalf.
- **Already-WebP input is a decision, not a given.** The reference set here treats WebP as
  non-convertible and passes it through. That is right for a fresh upload path and wrong for a
  backfill whose stored images are already WebP at capture resolution: leaving them alone means the
  pass does nothing. Add `image/webp` and `.webp` to the convertible set when re-encoding is the point,
  and rely on the size guard to make it safe.
- **Detection accepts either signal, case-insensitively.** Clients post `image/jpg`, `IMAGE/PNG`, or
  `application/octet-stream` with a `.PNG` filename, and a browser drag-and-drop can send no content
  type at all. Requiring both signals to agree rejects normal traffic.

Back to the index: [imagesharp-webp](imagesharp-webp.md)
