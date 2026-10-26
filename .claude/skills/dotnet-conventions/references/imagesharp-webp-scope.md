# When to convert to WebP in-process, and what to install

Shrink a JPEG or PNG the moment it arrives, before it is stored, and never damage anything else that
arrives with it. A real 351 KB PNG came back as a 71 KB WebP through this kind of converter.

## When to use

- An API accepts image uploads and you want one canonical, small format on disk or in the database.
- The conversion has to be safe for arbitrary input: the same endpoint also receives PDFs, SVGs,
  zero-byte files and JPEGs that are secretly something else.

Build-time conversion of a folder of site assets is a different job with different tools; that is
the `optimize-images` skill. This leaf is the in-process, per-request conversion.

## Packages

```xml
<PackageReference Include="SkiaSharp" Version="4.153.1" />
<PackageReference Include="SkiaSharp.NativeAssets.Linux.NoDependencies" Version="4.153.1" />
```

The native-assets package carries `libSkiaSharp` for Linux containers with no system dependencies,
so the Dockerfile needs no `apt` step for it. Keep both packages on the same version, and pin the
version already used elsewhere in the solution rather than taking whatever is newest.

## Related

- [`sql-stored-files`](sql-stored-files.md) - where the converted bytes come to rest, and the endpoint that serves them back.
- [`file-import-ingest`](file-import-ingest.md) - the upload endpoint shape and `IFormFile` buffering.
- `optimize-images` (global skill) - build-time conversion of a folder of site assets, and the same encode-both-and-keep-the-smaller rule applied there.

Back to the index: [imagesharp-webp](imagesharp-webp.md)
