from typing import List, Optional

import typer
from db import get_connection, init_db

app = typer.Typer()
tag_app = typer.Typer(help="Manage tags on a note")
app.add_typer(tag_app, name="tag")


@app.callback(invoke_without_command=True)
def main():
    init_db()


def _print_rows(rows):
    for row in rows:
        print(f"{row[0]}  {row[1]}  {row[2]}")


@app.command()
def add(body: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO notes (body, created_at) VALUES (?, datetime('now'))",
        (body,),
    )
    conn.commit()
    conn.close()


@app.command(name="list")
def list_notes(tag: Optional[List[str]] = typer.Option(None, "--tag", help="Filter by tag, repeatable, AND semantics")):
    conn = get_connection()
    if tag:
        placeholders = ",".join("?" for _ in tag)
        sql = f"""
            SELECT n.id, n.created_at, n.body, n.pinned
            FROM notes n
            JOIN note_tags nt ON nt.note_id = n.id
            JOIN tags t ON t.id = nt.tag_id
            WHERE t.name IN ({placeholders})
            GROUP BY n.id
            HAVING COUNT(DISTINCT nt.tag_id) = ?
            ORDER BY n.pinned DESC, n.id DESC
        """
        rows = conn.execute(sql, (*tag, len(set(tag)))).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, created_at, body, pinned FROM notes ORDER BY pinned DESC, id DESC"
        ).fetchall()
    conn.close()
    _print_rows(rows)


def _note_exists(conn, note_id: int) -> bool:
    return conn.execute("SELECT 1 FROM notes WHERE id = ?", (note_id,)).fetchone() is not None


@tag_app.command("add")
def tag_add(note_id: int, name: str):
    conn = get_connection()
    if not _note_exists(conn, note_id):
        conn.close()
        print(f"no note with id {note_id}")
        raise typer.Exit(code=1)
    conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (name,))
    tag_id = conn.execute("SELECT id FROM tags WHERE name = ?", (name,)).fetchone()[0]
    conn.execute(
        "INSERT OR IGNORE INTO note_tags (note_id, tag_id) VALUES (?, ?)",
        (note_id, tag_id),
    )
    conn.commit()
    conn.close()
    print(f"tagged note {note_id} with {name}")


@tag_app.command("remove")
def tag_remove(note_id: int, name: str):
    conn = get_connection()
    conn.execute(
        """
        DELETE FROM note_tags
        WHERE note_id = ?
          AND tag_id IN (SELECT id FROM tags WHERE name = ?)
        """,
        (note_id, name),
    )
    conn.commit()
    conn.close()
    print(f"removed {name} from note {note_id}")


def _set_pinned(note_id: int, value: int):
    conn = get_connection()
    if not _note_exists(conn, note_id):
        conn.close()
        print(f"no note with id {note_id}")
        raise typer.Exit(code=1)
    conn.execute("UPDATE notes SET pinned = ? WHERE id = ?", (value, note_id))
    conn.commit()
    conn.close()


@app.command()
def pin(note_id: int):
    _set_pinned(note_id, 1)
    print(f"pinned note {note_id}")


@app.command()
def unpin(note_id: int):
    _set_pinned(note_id, 0)
    print(f"unpinned note {note_id}")


if __name__ == "__main__":
    app()
