import typer
from db import get_connection, init_db

app = typer.Typer()


@app.callback(invoke_without_command=True)
def main():
    init_db()


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
def list_notes():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, created_at, body FROM notes ORDER BY id DESC"
    ).fetchall()
    conn.close()
    for row in rows:
        print(f"{row[0]}  {row[1]}  {row[2]}")


if __name__ == "__main__":
    app()
