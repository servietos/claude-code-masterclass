# Decompose a Spec into Independently Executable Work Packages

Nothing is delegated here and no second agent runs: this is a planning output, and the discipline is in the contracts rather than in who executes them. You split the work in STATE.md into three named packages, each with its input, its output contract and its declared dependencies, then audit every contract until it is a command you could run yourself.

------

## Split the Spec into Three Packages

Run this in the [notes-cli/](notes-cli/) starter once [demo-authoring-state.md](demo-authoring-state.md) has produced a STATE.md with an empty Open Questions section. Submit:

```text
Decompose the work in STATE.md into three work packages, each one small enough to hand to a
separate executor. For each:
  - name (short, lowercase, hyphenated)
  - input: the files it may read and the section of STATE.md that governs it
  - output: the files it creates or modifies and the contract it must satisfy (a callable command
    plus the expected output)
  - depends on: which other package must finish first, if any

The three packages:
  1. fts5-migration: adds the FTS5 virtual table without dropping existing notes rows
  2. search-command: implements search "query" printing results ranked by BM25
  3. tests: writes a test file that verifies the migration survived and search returns ranked results

Return a markdown table. Do not implement anything yet.
```

## Audit Each Contract for Runnability

Check the table before executing anything: each contract must be a command you could run yourself, `search-command` must depend on `fts5-migration`, and `tests` must depend on both. A package whose contract reads like a description of intent is not checkable; send it back and ask for a command.

The three packages executed end to end, including the tests they produce, are in [notes-cli-solution/](notes-cli-solution/).
