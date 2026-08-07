# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "mcp>=1.9.0",
# ]
# ///

import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("EventTrack")

DB_PATH = Path(__file__).parent / "events.db"


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                description TEXT,
                date        TEXT NOT NULL,
                venue       TEXT NOT NULL,
                capacity    INTEGER NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS registrations (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id      INTEGER NOT NULL REFERENCES events(id),
                name          TEXT NOT NULL,
                email         TEXT NOT NULL,
                registered_at TEXT NOT NULL,
                UNIQUE(event_id, email)
            )
            """
        )

        if conn.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO events (title, description, date, venue, capacity) VALUES (?, ?, ?, ?, ?)",
                [
                    (
                        "Keynote: The Future of AI Agents",
                        "Opening keynote on where agentic systems are heading.",
                        "2026-09-15",
                        "Main Hall",
                        300,
                    ),
                    (
                        "Workshop: Building MCP Servers in Python",
                        "Hands-on session building an MCP server with FastMCP.",
                        "2026-09-15",
                        "Room A",
                        30,
                    ),
                    (
                        "Workshop: Claude Code for Agentic Workflows",
                        "Practical agentic workflows with Claude Code.",
                        "2026-09-16",
                        "Room B",
                        30,
                    ),
                    (
                        "Panel: Ethics in AI-Assisted Engineering",
                        "Panel discussion on responsible AI-assisted engineering.",
                        "2026-09-16",
                        "Main Hall",
                        200,
                    ),
                    (
                        "Hands-On Lab: FastAPI + Claude Integration",
                        "Build a FastAPI service that talks to Claude.",
                        "2026-09-17",
                        "Lab Room",
                        20,
                    ),
                ],
            )
            conn.executemany(
                "INSERT INTO registrations (event_id, name, email, registered_at) VALUES (?, ?, ?, ?)",
                [
                    (1, "Maria Lindqvist", "maria.lindqvist@example.com", "2026-08-01T09:12:00+00:00"),
                    (1, "Tom Beckett", "tom.beckett@example.com", "2026-08-01T10:45:00+00:00"),
                    (2, "Anita Raman", "anita.raman@example.com", "2026-08-02T08:30:00+00:00"),
                    (2, "Felix Warner", "felix.warner@example.com", "2026-08-02T14:05:00+00:00"),
                    (3, "Sofia Moretti", "sofia.moretti@example.com", "2026-08-03T11:20:00+00:00"),
                    (3, "Daniel Osei", "daniel.osei@example.com", "2026-08-04T16:50:00+00:00"),
                ],
            )


@mcp.tool()
def list_events() -> list[dict]:
    """List all events with venue, date, capacity and remaining seats."""
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT e.id, e.title, e.description, e.date, e.venue, e.capacity,
                   (SELECT COUNT(*) FROM registrations r WHERE r.event_id = e.id) AS registered_count
            FROM events e
            ORDER BY e.date, e.title
            """
        ).fetchall()

    return [
        {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "date": row["date"],
            "venue": row["venue"],
            "capacity": row["capacity"],
            "registered_count": row["registered_count"],
            "seats_remaining": row["capacity"] - row["registered_count"],
        }
        for row in rows
    ]


@mcp.tool()
def create_event(title: str, description: str, date: str, venue: str, capacity: int) -> dict:
    """Create a new event with a capacity limit."""
    if capacity < 1:
        return {"error": "Capacity must be at least 1"}
    if not date.strip():
        return {"error": "Date must be a non-empty string"}

    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO events (title, description, date, venue, capacity) VALUES (?, ?, ?, ?, ?)",
            (title, description, date, venue, capacity),
        )
        event_id = cursor.lastrowid

    return {"id": event_id, "title": title, "status": "created"}


@mcp.tool()
def check_availability(event_id: int) -> dict:
    """Return remaining seats for one event."""
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT e.id, e.title, e.capacity,
                   (SELECT COUNT(*) FROM registrations r WHERE r.event_id = e.id) AS registered_count
            FROM events e
            WHERE e.id = ?
            """,
            (event_id,),
        ).fetchone()

    if row is None:
        return {"error": "Event not found"}

    seats_remaining = row["capacity"] - row["registered_count"]
    return {
        "event_id": row["id"],
        "title": row["title"],
        "capacity": row["capacity"],
        "registered_count": row["registered_count"],
        "seats_remaining": seats_remaining,
        "is_full": seats_remaining <= 0,
    }


@mcp.tool()
def register_attendee(event_id: int, name: str, email: str) -> dict:
    """Register an attendee for an event; rejects a full event or a duplicate e-mail."""
    if not name.strip():
        return {"error": "Name must be a non-empty string"}
    if not email.strip():
        return {"error": "Email must be a non-empty string"}

    availability = check_availability(event_id)
    if "error" in availability:
        return availability
    if availability["seats_remaining"] == 0:
        return {"error": "Event is full"}

    registered_at = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        try:
            conn.execute(
                "INSERT INTO registrations (event_id, name, email, registered_at) VALUES (?, ?, ?, ?)",
                (event_id, name, email, registered_at),
            )
        except sqlite3.IntegrityError:
            return {"error": "Already registered"}

    return {
        "event_id": event_id,
        "event_title": availability["title"],
        "name": name,
        "email": email,
        "registered_at": registered_at,
    }


@mcp.tool()
def list_registrations(event_id: int | None = None) -> list[dict]:
    """List registrations for one event, or for all events when no event_id is given."""
    query = """
        SELECT r.id AS registration_id, r.event_id, e.title AS event_title,
               r.name, r.email, r.registered_at
        FROM registrations r
        JOIN events e ON e.id = r.event_id
    """
    params: tuple = ()
    if event_id is not None:
        query += " WHERE r.event_id = ?"
        params = (event_id,)
    query += " ORDER BY e.date, r.registered_at"

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()

    return [dict(row) for row in rows]


@mcp.tool()
def cancel_registration(event_id: int, email: str) -> dict:
    """Cancel a registration by event and attendee e-mail."""
    with get_db() as conn:
        cursor = conn.execute(
            "DELETE FROM registrations WHERE event_id = ? AND email = ?",
            (event_id, email),
        )
        deleted = cursor.rowcount

    if deleted == 0:
        return {"error": "Registration not found"}

    return {"event_id": event_id, "email": email, "status": "cancelled"}


@mcp.tool()
def get_event_summary(event_id: int) -> dict:
    """Return registration statistics and the attendee list for one event."""
    with get_db() as conn:
        event = conn.execute(
            "SELECT id, title, date, venue, capacity FROM events WHERE id = ?",
            (event_id,),
        ).fetchone()

        if event is None:
            return {"error": "Event not found"}

        attendees = conn.execute(
            "SELECT name, email FROM registrations WHERE event_id = ? ORDER BY registered_at",
            (event_id,),
        ).fetchall()

    registered_count = len(attendees)
    seats_remaining = event["capacity"] - registered_count
    return {
        "event_id": event["id"],
        "title": event["title"],
        "date": event["date"],
        "venue": event["venue"],
        "capacity": event["capacity"],
        "registered_count": registered_count,
        "seats_remaining": seats_remaining,
        "is_full": seats_remaining <= 0,
        "attendees": [dict(row) for row in attendees],
    }


if __name__ == "__main__":
    if "--stdio" in sys.argv:
        init_db()
        mcp.run(transport="stdio")
    else:
        print("Usage: uv run server.py --stdio")
        sys.exit(0)
