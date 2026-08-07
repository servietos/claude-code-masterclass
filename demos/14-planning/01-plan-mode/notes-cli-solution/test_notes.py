import sqlite3

import pytest
from typer.testing import CliRunner

import db
from notes import app


@pytest.fixture
def cli(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "notes.db"))
    return CliRunner()


def test_list_prints_added_notes(cli):
    cli.invoke(app, ["add", "hello from notes-cli"])
    cli.invoke(app, ["add", "second note"])
    result = cli.invoke(app, ["list"])
    assert "hello from notes-cli" in result.stdout
    assert "second note" in result.stdout


def test_search_returns_matching_note_only(cli):
    cli.invoke(app, ["add", "hello from notes-cli"])
    cli.invoke(app, ["add", "second note"])
    result = cli.invoke(app, ["search", "hello"])
    assert "hello from notes-cli" in result.stdout
    assert "second note" not in result.stdout


def test_search_ranks_denser_match_first(cli):
    cli.invoke(app, ["add", "sqlite mentioned once"])
    cli.invoke(app, ["add", "sqlite sqlite sqlite"])
    result = cli.invoke(app, ["search", "sqlite"])
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert "sqlite sqlite sqlite" in lines[0]


def test_existing_rows_survive_migration(cli):
    legacy = sqlite3.connect(db.DB_PATH)
    legacy.execute(
        "CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT NOT NULL, created_at TEXT NOT NULL)"
    )
    legacy.execute(
        "INSERT INTO notes (body, created_at) VALUES ('legacy note about planning', datetime('now'))"
    )
    legacy.commit()
    legacy.close()

    result = cli.invoke(app, ["search", "planning"])
    assert "legacy note about planning" in result.stdout

    listed = cli.invoke(app, ["list"])
    assert "legacy note about planning" in listed.stdout
