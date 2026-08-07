---
presents: demo-work-package-decomposition.md
budget: 4 min
beats: 4
---

# Present: Decompose a Spec into Independently Executable Work Packages

A work package is four fields, and only the contract is hard. A contract is only a contract when it is a command someone can run without reading the source. Four beats: the fields, declared dependencies, the contract as a Done Criteria bullet, the contract as printed output.

------

## Beats

### Beat 1: a package is four fields, and only one of them is hard (1 min)

**Open:** [Split the Spec into Three Packages](demo-work-package-decomposition.md#split-the-spec-into-three-packages) · [Decomposition Rules](readme.md#decomposition-rules)
**Say:** A package is a unit one session can finish without coming back to ask a question. The contract is the only field a reviewer can check without opening the source.

```text
Decompose the work in STATE.md into three work packages, each one small enough to hand to a
separate executor. For each:
  - name (short, lowercase, hyphenated)
  - input: the files it may read and the section of STATE.md that governs it
  - output: the files it creates or modifies and the contract it must satisfy (a callable command
    plus the expected output)
  - depends on: which other package must finish first, if any
```

**Result:** the package names became the Status list in [`notes-cli-solution/STATE.md`](notes-cli-solution/STATE.md)

```markdown
- [x] FTS5 migration
- [x] search command
- [x] tests
```

**Gotcha:** each package targets one concern, which is rarely one file; three to five is the working range.

### Beat 2: dependencies are declared, never inferred (1 min)

**Open:** [`notes-cli/db.py`](notes-cli/db.py) · [`notes-cli/notes.py`](notes-cli/notes.py)
**Say:** An executor sees its own package and nothing else, so ordering exists only if somebody wrote it down. Declaring it is also what makes parallelism visible.

```text
The three packages:
  1. fts5-migration: adds the FTS5 virtual table without dropping existing notes rows
  2. search-command: implements search "query" printing results ranked by BM25
  3. tests: writes a test file that verifies the migration survived and search returns ranked results

Return a markdown table. Do not implement anything yet.
```

**Result:** the declared chain is visible in the code; [`notes-cli-solution/notes.py`](notes-cli-solution/notes.py) selects from the table the `fts5-migration` package created

```python
        FROM notes_fts
        JOIN notes ON notes.id = notes_fts.rowid
```

**Gotcha:** this is the beat for the push back; a contract that reads like a description of intent goes straight back with "give me the command".

### Beat 3: the contract becomes a Done Criteria bullet (1 min)

**Open:** [`notes-cli-solution/STATE.md`](notes-cli-solution/STATE.md) · the `Done Criteria` section
**Say:** A contract counts once it survives leaving the package that defined it, and the statefile is where it lands. Anything needing interpretation to call PASS or FAIL will be called PASS.

```markdown
## Done Criteria
- `python notes.py search "hello"` returns matching notes ranked by BM25
- `python notes.py list` still works and returns all notes
- Existing seed notes survive the migration
- `python test_notes.py` prints three PASS lines and exits 0
```

**Result:** the fourth bullet arrived with the `tests` package, and [`notes-cli-solution/test_notes.py`](notes-cli-solution/test_notes.py) exists only in the solution

```text
PASS migration keeps existing rows
PASS search ranks by bm25
PASS cli search and list
```

**Gotcha:** the first three bullets were written during planning; the shape to hold everything to is a command, an output and an exit code.

### Beat 4: the contract is literally what the file prints (1 min)

**Open:** [`notes-cli-solution/test_notes.py`](notes-cli-solution/test_notes.py) · `main()` · `notes.db` (built by this run inside a temporary directory)
**Say:** The proof a contract was real is that someone who never read the plan can execute it, with nothing installed beyond what the project already uses.

```python
def main():
    workdir = tempfile.mkdtemp()
    path = os.path.join(workdir, "notes.db")
    build_legacy_db(path)
    test_migration_keeps_existing_rows(path)
    print("PASS migration keeps existing rows")
    test_search_ranks_by_bm25(path)
    print("PASS search ranks by bm25")
```

**Result:** the "existing rows survive" contract forced a probe and a guarded rebuild into [`notes-cli-solution/db.py`](notes-cli-solution/db.py)

```diff
+    fts_exists = conn.execute(
+        "SELECT name FROM sqlite_master WHERE type='table' AND name='notes_fts'"
+    ).fetchone()
...
+    if fts_exists is None:
+        conn.execute("INSERT INTO notes_fts (notes_fts) VALUES ('rebuild')")
     conn.commit()
     conn.close()
```

**Gotcha:** `build_legacy_db` is the interesting call; it creates a database with no FTS index, so the migration is tested against the legacy shape rather than a fresh one.

## If the room asks

| Question | Answer |
|---|---|
| Is this delegation? | No. Nothing is implemented and no second agent runs. |
| Why three packages and not seven? | Three to five is the working range; past seven the coordination cost exceeds the parallelism. |
| How do I know a contract is good enough? | You can run it without reading the source. If checking it means opening the implementation, it is a description. |
| Can the three packages run in parallel? | Not these. `search-command` needs the FTS table and `tests` needs both, so the chain is serial by declaration. |
| What if Claude returns prose instead of a table? | Ask again for the table with the four fields; the tabular shape is what makes a missing contract visible. |
