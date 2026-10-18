from datetime import date, timedelta

from db import get_connection
from fees import late_fee_cents


def add_bike(label, frame_size):
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO bikes (label, frame_size) VALUES (?, ?)", (label, frame_size)
        )
        return cur.lastrowid


def find_or_create_customer(name, phone):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM customers WHERE phone = ?", (phone,)
        ).fetchone()
        if row:
            return row["id"]
        cur = conn.execute(
            "INSERT INTO customers (name, phone) VALUES (?, ?)", (name, phone)
        )
        return cur.lastrowid


def rent_bike(label, name, phone, days):
    today = date.today()
    due = today + timedelta(days=days)
    customer_id = find_or_create_customer(name, phone)
    with get_connection() as conn:
        bike = conn.execute(
            "SELECT id, status FROM bikes WHERE label = ?", (label,)
        ).fetchone()
        if bike is None:
            raise ValueError(f"no bike {label}")
        if bike["status"] != "available":
            raise ValueError(f"bike {label} is {bike['status']}")
        conn.execute(
            "INSERT INTO rentals (bike_id, customer_id, rented_at, due_at) VALUES (?, ?, ?, ?)",
            (bike["id"], customer_id, today.isoformat(), due.isoformat()),
        )
        conn.execute("UPDATE bikes SET status = 'rented' WHERE id = ?", (bike["id"],))
    return due


def return_bike(label):
    today = date.today()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT r.id, r.due_at FROM rentals r JOIN bikes b ON b.id = r.bike_id "
            "WHERE b.label = ? AND r.returned_at IS NULL",
            (label,),
        ).fetchone()
        if row is None:
            raise ValueError(f"bike {label} is not rented")
        fee = late_fee_cents(date.fromisoformat(row["due_at"]), today)
        conn.execute(
            "UPDATE rentals SET returned_at = ?, late_fee_cents = ? WHERE id = ?",
            (today.isoformat(), fee, row["id"]),
        )
        conn.execute("UPDATE bikes SET status = 'available' WHERE label = ?", (label,))
    return fee


def list_open():
    with get_connection() as conn:
        return conn.execute(
            "SELECT b.label, c.name, c.phone, r.due_at FROM rentals r "
            "JOIN bikes b ON b.id = r.bike_id JOIN customers c ON c.id = r.customer_id "
            "WHERE r.returned_at IS NULL ORDER BY r.due_at"
        ).fetchall()
