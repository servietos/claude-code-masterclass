# Import Ingest: Extraction and the AI Client

### 2. Extraction — content-type fork (Excel / text-PDF / image)

Uploaded files come in three physical shapes; branch on content type:

| Input | Extraction |
|---|---|
| `.xlsx` | Read cells server-side (**EPPlus**) into a row/column grid. |
| text-layer PDF | **UglyToad.PdfPig** — `PdfDocument.Open`, bucket words into rows by rounded `BoundingBox.Bottom`, emit `\t` when the x-gap exceeds a threshold to preserve columns. |
| image / scanned PDF | Pass raw bytes to a **vision model** (`image_url` data-URI content part). Files with no text layer need OCR via the vision model, not PdfPig. |

EPPlus 5 and later refuses to read a workbook until `ExcelPackage.LicenseContext = LicenseContext.NonCommercial`
(or the licensed equivalent) is set once at startup, before the first `ExcelPackage` is created.

Then hand the reconstructed text (or image) to the AI with a **strict JSON-schema system prompt** and `response_format = { type: "json_object" }`, and deserialize case-insensitively into a POCO:

```csharp
var json = await ai.CompleteAsync(messages, json: true, image: imageBytes, preferVision: isImage);
var doc  = JsonSerializer.Deserialize<ExtractedSheet>(json,
              new JsonSerializerOptions { PropertyNameCaseInsensitive = true })
           ?? throw new InvalidOperationException("Empty extraction response");
```

> **Why AI mapping, not a fixed parser:** every source spreadsheet uses different headers — the
> same "customer name" column might be called `Name`, `Full Name`, or `Kunde` across files. The
> system prompt describes the *target* fields and lets the model map whatever columns arrive. Bake
> locale rules (date formats, phone formats, honorifics) into the prompt where the domain needs them.

### 3. Reuse the app's existing AI client — do NOT add a new SDK

If the app already talks to an OpenAI-compatible chat model, reuse that client/abstraction for the
extraction and assist calls rather than adding a second SDK:

- Provider-agnostic `/chat/completions` over `IHttpClientFactory` (model catalog + keys resolved at runtime, not hardcoded in `appsettings`).
- `json` switch → `response_format=json_object`; `image`/`preferVision` switches for vision.
- Keep the AI-call methods `virtual` and `InternalsVisibleTo` the test project so they mock cleanly.
- Read all config through a strongly-typed config class, never raw `IConfiguration`.

Back to the index: [file-import-ingest](file-import-ingest.md)
