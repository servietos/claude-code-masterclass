---
description: Generate documentation for a code file at a given path, then run brand-voice and code-reviewer over the output before saving.
argument-hint: <path-to-code-file>
allowed-tools: Read, Write, Edit, Glob, Grep
---

# /create-docs

Generate human-readable documentation for the source file at `$ARGUMENTS`. The command produces a `<filename>.md` sibling document, then chains the plugin's `brand-voice` and `code-reviewer` skills to enforce quality on the documentation and the code itself.

## Inputs

A single argument: the absolute or repo-relative path to a source file. If the argument is missing, ask for it before proceeding. If the path does not exist, stop and surface the error rather than guessing.

## Workflow

1. Read the source file at `$ARGUMENTS` end to end. Do not paginate; the documentation must reflect the whole file.
2. Extract: module purpose, public surface (exported functions, classes, constants), inputs and outputs per function, side effects, and any non-obvious invariants.
3. Write the documentation to `<source-path>.md` (same directory, `.md` appended) using the structure below.
4. Invoke the `code-quality-plugin:brand-voice` skill against the generated file to enforce em-dash, paragraph length, and Mermaid label rules.
5. Invoke the `code-quality-plugin:code-reviewer` skill against the original source file. Surface critical findings inline in the generated doc under a "Review Notes" section.
6. Print a one-line summary: documented file, brand-voice violations fixed, review findings count by severity.

## Output Structure

The generated markdown file must contain these sections in order:

```markdown
# <Module name>

## Purpose
One paragraph describing what the module does and when to use it.

## Public Surface
Table: Symbol | Kind | Signature | Description.

## Behavior Notes
Bulleted list of side effects, invariants, and non-obvious assumptions.

## Usage
A minimal runnable example in a fenced code block.

## Review Notes
Findings from the code-reviewer skill, grouped by severity.
```

## Rules

- Reference symbols with `file_path:line_number` so the reader can jump straight to the source.
- Do not paraphrase docstrings that already exist verbatim; quote them in a fenced block instead.
- Keep paragraphs under four sentences; the brand-voice pass will fail otherwise.
- Never modify the source file. The command is read-only against the input and only writes the documentation file.
