import sqlite3

DB_PATH = "notes.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY,
            body TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    columns = [row[1] for row in conn.execute("PRAGMA table_info(notes)")]
    if "pinned" not in columns:
        conn.execute("ALTER TABLE notes ADD COLUMN pinned INTEGER NOT NULL DEFAULT 0")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS note_tags (
            note_id INTEGER NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
            tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
            PRIMARY KEY (note_id, tag_id)
        )
    """)
    conn.commit()
    conn.close()


def tag_id_for(conn, name):
    conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (name,))
    return conn.execute("SELECT id FROM tags WHERE name = ?", (name,)).fetchone()[0]


def tags_for(conn, note_id):
    rows = conn.execute(
        """
        SELECT tags.name FROM tags
        JOIN note_tags ON note_tags.tag_id = tags.id
        WHERE note_tags.note_id = ?
        ORDER BY tags.name
        """,
        (note_id,),
    ).fetchall()
    return [row[0] for row in rows]
