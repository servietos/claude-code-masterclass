---
presents: demo-spec-kit-pipeline.md
budget: 4 min
beats: 4
---

# Present: Run a Feature Through the Four-Step Spec Kit Pipeline

Spec Kit's value is the enforced split between principles, spec and plan. A spec that mentions tables is the failure the pipeline exists to catch. Four beats: the constitution, the split, the comparison against a hand-written STATE.md, the query shape in the code.

------

**Shell:** setup ships twice, [`setup-speckit.ps1`](setup-speckit.ps1) on Windows and [`setup-speckit.sh`](setup-speckit.sh) elsewhere; both copy the starter to `~/spec-runs/notes-cli-speckit`, outside this checkout because Spec Kit initialises its own git repository. The beats themselves quote no shell, only skills invoked inside the session.

## Beats

### Beat 1: the constitution is the step that makes the later steps behave (1 min)

**Open:** [Part A: Lock the Principles](demo-spec-kit-pipeline.md#part-a-lock-the-principles) · [`setup-speckit.ps1`](setup-speckit.ps1)
**Say:** Governing principles are what every team believes it shares and nobody writes down. Written before any feature exists, each later step reads them, so the constraint is applied rather than remembered.

```text
/speckit-constitution Principles: 1. Python stdlib only beyond Typer. 2. Storage is SQLite via sqlite3, no ORM. 3. Every command must be testable in isolation. 4. Existing notes.db rows survive all schema changes. 5. CLI surface stays small: at most two new commands per feature.
```

**Result:** the constitution file lands in the run folder outside this checkout, so it is not linkable; principle 4 survives into [`notes-cli-solution/db.py`](notes-cli-solution/db.py) as a probe before the `ALTER TABLE`

```diff
     """)
+    columns = [row[1] for row in conn.execute("PRAGMA table_info(notes)")]
+    if "pinned" not in columns:
+        conn.execute("ALTER TABLE notes ADD COLUMN pinned INTEGER NOT NULL DEFAULT 0")
```

**Gotcha:** nobody tells `plan` to make the migration idempotent; the constitution does, in a file written long before it.

### Beat 2: specify stays user-facing, plan carries the schema (1.5 min)

**Open:** [Part B: Specify, Plan, Tasks](demo-spec-kit-pipeline.md#part-b-specify-plan-tasks) · [`notes-cli/db.py`](notes-cli/db.py) · `specs/<feature>/spec.md` (written by `/speckit-specify` into the run folder outside this checkout)
**Say:** What the software does for a user and how it is built have two different readers. Keeping schema out of the first is what makes it approvable by someone outside engineering.

```text
/speckit-specify Add tag-based search and pinning to notes-cli. Users attach tags to notes, search with AND semantics across multiple tags, and mark notes pinned so they sort first. Existing notes without tags or pins work unchanged.
...
/speckit-plan Tech stack: Python 3.12, Typer, sqlite3 stdlib. Tags: normalised table plus junction table, no JSON columns. Pinned: integer column on notes (default 0). Multi-tag query: GROUP BY note_id HAVING COUNT(DISTINCT tag_id) = N. List order: pinned DESC, id DESC. Migration runs idempotently on startup.
```

**Result:** the plan's "normalised table plus junction table" reached [`notes-cli-solution/db.py`](notes-cli-solution/db.py); the spec names no table at all

```python
    conn.execute("""
        CREATE TABLE IF NOT EXISTS note_tags (
            note_id INTEGER NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
            tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
            PRIMARY KEY (note_id, tag_id)
        )
```

**Gotcha:** read `spec.md` before running `tasks`; schema decisions leaked upward into the spec are the failure this pipeline exists to prevent.

### Beat 3: hold the generated spec against a hand-written STATE.md (1 min)

**Open:** [Part C: Implement and Compare](demo-spec-kit-pipeline.md#part-c-implement-and-compare) · [`../02-extended-thinking/notes-cli-solution/STATE.md`](../02-extended-thinking/notes-cli-solution/STATE.md)
**Say:** Both traditions carry the same logical content, so the honest comparison is cost to produce against distance travelled. That makes it a question about who reads next.

```text
Compare specs/<feature>/spec.md against the STATE.md I wrote by hand. Answer three questions:
  1. Which document is more verbose, and which audience is each written for?
  2. Where did the schema decisions end up in each approach?
  3. Which one would survive being handed to someone who has never seen this project?
```

**Result:** the comparison is the deliverable and stays in the session, with no file to link. The hand-written counterpart is 31 lines in one file, carrying goal, decisions, status and criteria together; Spec Kit splits the same content across four artefacts.

**Gotcha:** the demo's payload is the comparison, not the generated tree.

### Beat 4: the plan's query shape lands verbatim in the code (0.5 min)

**Open:** [Spec Kit](readme.md#spec-kit) · `plan.md` (the `/speckit-plan` output, in the run folder outside this checkout)
**Say:** Traceability is what a spec pipeline is selling, so it is tested against finished source rather than against the task list that promised it.

```python
        SELECT notes.id, notes.created_at, notes.body, notes.pinned FROM notes
        JOIN note_tags ON note_tags.note_id = notes.id
        JOIN tags ON tags.id = note_tags.tag_id
        WHERE tags.name IN ({placeholders})
        GROUP BY notes.id
        HAVING COUNT(DISTINCT tags.id) = ?
        ORDER BY notes.pinned DESC, notes.id DESC
```

**Result:** the same `pinned DESC, id DESC` reached `list` in [`notes-cli-solution/notes.py`](notes-cli-solution/notes.py)

```python
        "SELECT id, created_at, body, pinned FROM notes ORDER BY pinned DESC, id DESC"
```

**Gotcha:** `GROUP BY` plus `HAVING COUNT(DISTINCT ...) = N` is the AND-semantics decision from the plan step, unchanged.

## If the room asks

| Question | Answer |
|---|---|
| Are these slash commands? | No, skills. Confirm with `/skills` and look for `speckit-constitution`, `speckit-specify`, `speckit-plan`, `speckit-tasks`, `speckit-implement`. |
| Why does the run folder live outside the repository? | Spec Kit initialises its own git repository and writes a tree of files; the setup script keeps this checkout clean. |
| Can I skip the constitution on a familiar domain? | By hand you would. The framework removes the option, which is worth most on domains you do not know. |
| Is the overhead worth it? | Not on a one-hour feature. On a two-day migration, or when a second person reads the artefacts, it pays for itself. |
| What are `speckit-clarify` and `speckit-analyze`? | Optional: `clarify` asks structured questions before `plan`, `analyze` produces a cross-artefact consistency report after `tasks`. |
