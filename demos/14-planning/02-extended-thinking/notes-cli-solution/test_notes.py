import os
import sqlite3
import subprocess
import sys
import tempfile

import db

SEED = ["hello world", "second note", "hello again hello"]


def build_legacy_db(path):
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE notes (
            id INTEGER PRIMARY KEY,
            body TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.executemany(
        "INSERT INTO notes (body, created_at) VALUES (?, datetime('now'))",
        [(body,) for body in SEED],
    )
    conn.commit()
    conn.close()


def test_migration_keeps_existing_rows(path):
    db.DB_PATH = path
    db.init_db()
    conn = sqlite3.connect(path)
    bodies = [row[0] for row in conn.execute("SELECT body FROM notes ORDER BY id")]
    indexed = conn.execute(
        "SELECT count(*) FROM notes_fts WHERE notes_fts MATCH 'hello OR second'"
    ).fetchone()[0]
    conn.close()
    assert bodies == SEED
    assert indexed == len(SEED)


def test_search_ranks_by_bm25(path):
    conn = sqlite3.connect(path)
    rows = conn.execute(
        """
        SELECT notes.body
        FROM notes_fts
        JOIN notes ON notes.id = notes_fts.rowid
        WHERE notes_fts MATCH 'hello'
        ORDER BY bm25(notes_fts) ASC
        """
    ).fetchall()
    conn.close()
    assert [row[0] for row in rows] == ["hello again hello", "hello world"]


def test_cli_search_and_list(workdir):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notes.py")

    def run(args):
        return subprocess.run(
            [sys.executable, script] + args,
            cwd=workdir,
            capture_output=True,
            text=True,
            env=env,
        )

    run(["add", "hello world"])
    run(["add", "second note"])
    search = run(["search", "hello"])
    listed = run(["list"])
    assert search.returncode == 0
    assert "hello world" in search.stdout
    assert "second note" not in search.stdout
    assert listed.stdout.count("\n") == 2


def main():
    workdir = tempfile.mkdtemp()
    path = os.path.join(workdir, "notes.db")
    build_legacy_db(path)
    test_migration_keeps_existing_rows(path)
    print("PASS migration keeps existing rows")
    test_search_ranks_by_bm25(path)
    print("PASS search ranks by bm25")
    test_cli_search_and_list(tempfile.mkdtemp())
    print("PASS cli search and list")


if __name__ == "__main__":
    main()
