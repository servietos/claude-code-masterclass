# Gate 4: format fidelity for parsers and serializers

## Gate 4 — Format fidelity, for anything that parses or serializes

An editor, formatter, or converter that round-trips content through its own AST will silently
rewrite everything its AST cannot model. Before adopting one, inventory what the stored format
actually contains beyond the standard:

- non-standard block syntax (Hugo shortcodes `{{< media-block >}}`, MDX, Liquid, Jinja)
- raw HTML embedded in markdown
- front matter
- whitespace or line endings that another system asserts on

Every ProseMirror-based markdown editor (Milkdown/Crepe, Tiptap, Toast UI) fails this gate for
such content unless you write a custom node spec per construct. A **source** editor
(CodeMirror 6) does not have the failure mode at all: the document is the text.

Second half of the gate: who else writes the document? If an AI agent or a sibling editor replaces
the whole document, a WYSIWYG's internal state and undo history fight that write path, and the
guard you need (apply an external change only when the incoming text differs from the current doc)
is far easier to get right on a text editor than on an AST editor.

Back to the index: [angular-dependency-evaluation](angular-dependency-evaluation.md)
