# Worked example: the admin markdown editor

## Worked example (2026-08-16, `src/admin.integrations.at`)

Question: replace the article editor's `<textarea>` with a good maintained markdown editor?

- Gate 1: `@codemirror/lang-markdown` 6.5.2 published 12 days prior, 4.2M/week. `@toast-ui/editor`
  last published 2023-02-17, dead despite 227k/week. `easymde` alive but still CodeMirror **5**.
- Gate 2: every Angular wrapper dead (table above), so CodeMirror 6 used directly.
- Gate 3: app initial bundle 419 kB raw / 109 kB gzip against a 500 kB warning. CodeMirror +
  markdown = 526 kB raw / 181 kB gzip, so it must be lazy. Crepe = 2675 kB raw / 898 kB gzip,
  unaffordable either way.
- Gate 4: the source carries YAML front matter, raw `<figure class="blog-img--hero">` HTML, and
  Hugo `{{< split-block >}}` / `{{< media-block >}}` shortcodes, and a chat agent rewrites the
  whole document each turn. Every WYSIWYG candidate eliminated here.

Verdict: adopt CodeMirror 6 as a source editor behind a dynamic `import()`, reject the WYSIWYG
class entirely. Half a day to a day.


Back to the index: [angular-dependency-evaluation](angular-dependency-evaluation.md)
