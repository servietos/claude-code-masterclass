# Encode both and measure, or encode once

How to tune the encode step in the converter above.

**"Optimal" means encoding twice and measuring, not picking a mode.** Which one wins is a property
of the picture, not of the format: photographic noise favours lossy, flat colour art and screenshots
favour lossless. The verified case here, a real screenshot-like PNG, came back **lossless** at
roughly a fifth of its original size, which is the opposite of what a lossy-by-default converter
would have produced. Encoding both costs milliseconds on an upload path that is already doing IO.

**Encoding twice is a default, not a requirement, and it is the pass's dominant cost.** On a folder of
web-sized uploads the second encode is milliseconds. On a backfill of 228 rows whose largest images
were 3584x4800, the lossless arm turned a seconds-long job into a multi-minute one and drew a "wtf
takes 15 minutes to optimize 20 images". When the user asks for one conversion, ship one lossy encode
at the quality they named and keep only the size guard below. Weigh this section against their
sentence rather than treating it as a rule that outranks it.

**A converter that can grow the file is a bug.** Lossy WebP regularly exceeds the source on
flat-colour art, so the size comparison against the original bytes is not an optimisation, it is the
guard that stops the endpoint from making uploads worse. When it fires, return the original bytes,
name and content type untouched.

Back to the index: [imagesharp-webp](imagesharp-webp.md)
