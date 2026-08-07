from typing import List

import typer

from db import get_connection, init_db, tag_id_for, tags_for

app = typer.Typer()


@app.callback(invoke_without_command=True)
def main():
    init_db()


def render(rows, conn):
    for note_id, created_at, body, pinned in rows:
        marker = "*" if pinned else " "
        tags = tags_for(conn, note_id)
        suffix = "  [" + ", ".join(tags) + "]" if tags else ""
        print(f"{marker} {note_id}  {created_at}  {body}{suffix}")


@app.command()
def add(body: str, tag: List[str] = typer.Option([], "--tag", "-t")):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO notes (body, created_at, pinned) VALUES (?, datetime('now'), 0)",
        (body,),
    )
    for name in tag:
        conn.execute(
            "INSERT OR IGNORE INTO note_tags (note_id, tag_id) VALUES (?, ?)",
            (cursor.lastrowid, tag_id_for(conn, name)),
        )
    conn.commit()
    conn.close()


@app.command(name="list")
def list_notes():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, created_at, body, pinned FROM notes ORDER BY pinned DESC, id DESC"
    ).fetchall()
    render(rows, conn)
    conn.close()


@app.command()
def search(tag: List[str] = typer.Option([], "--tag", "-t")):
    conn = get_connection()
    placeholders = ", ".join("?" for _ in tag)
    rows = conn.execute(
        f"""
        SELECT notes.id, notes.created_at, notes.body, notes.pinned FROM notes
        JOIN note_tags ON note_tags.note_id = notes.id
        JOIN tags ON tags.id = note_tags.tag_id
        WHERE tags.name IN ({placeholders})
        GROUP BY notes.id
        HAVING COUNT(DISTINCT tags.id) = ?
        ORDER BY notes.pinned DESC, notes.id DESC
        """,
        (*tag, len(tag)),
    ).fetchall()
    render(rows, conn)
    conn.close()


@app.command()
def pin(note_id: int):
    set_pinned(note_id, 1)


@app.command()
def unpin(note_id: int):
    set_pinned(note_id, 0)


def set_pinned(note_id, value):
    conn = get_connection()
    conn.execute("UPDATE notes SET pinned = ? WHERE id = ?", (value, note_id))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    app()
