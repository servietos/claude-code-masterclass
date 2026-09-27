# Wrapping the converter in a backfill tool

What applies when the converter is driven over existing rows rather than a live upload.

**A safety switch is a feature and needs its own ask.** A `--dry-run` default, an `--apply` flag, a
pre-write backup dump and a comparison report are each defensible and none of them were requested;
adding them unasked turned a one-line conversion into a tool with a manual, and every one of them was
cut. Build what the sentence describes.

**Where the column is a base64 string rather than `byte[]`**, wrap the byte converter instead of
forking it: decode, convert, re-encode, and pass an unparseable string straight back on
`FormatException` the same way undecodable bytes pass back on `ImageFormatException`. One
implementation, two entry points, so a backfill tool and the upload endpoint cannot drift. A tool that
lives outside the API project links that single file with
`<Compile Include="..\..\src\<api>\Services\WebpConverter.cs" />` rather than keeping a copy.

Back to the index: [imagesharp-webp](imagesharp-webp.md)
