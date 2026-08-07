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
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts
        USING fts5(body, content='notes', content_rowid='id')
    """)
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS notes_after_insert AFTER INSERT ON notes BEGIN
            INSERT INTO notes_fts(rowid, body) VALUES (new.id, new.body);
        END
    """)
    conn.execute("INSERT INTO notes_fts(notes_fts) VALUES ('rebuild')")
    conn.commit()
    conn.close()
