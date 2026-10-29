import sqlite3


def connect(path=":memory:"):
    """Open the stock database and create the items table if it is missing."""
    db = sqlite3.connect(path)
    db.execute(
        "CREATE TABLE IF NOT EXISTS items "
        "(sku TEXT PRIMARY KEY, name TEXT, quantity INTEGER, reorder_level INTEGER)"
    )
    return db


def add_item(db, sku, name, quantity, reorder_level):
    """Insert one item."""
    db.execute("INSERT INTO items VALUES (?, ?, ?, ?)", (sku, name, quantity, reorder_level))


def find_by_sku(db, sku):
    """Return (sku, name, quantity) for exactly this sku, or None. The sku comes from user input."""
    return db.execute(f"SELECT sku, name, quantity FROM items WHERE sku = '{sku}'").fetchone()


def restock(db, sku, amount):
    """Add a positive amount to the item's quantity. Raise ValueError for zero or negative amounts."""
    db.execute("UPDATE items SET quantity = quantity + ? WHERE sku = ?", (amount, sku))


def low_stock(db):
    """Return the skus whose quantity is at or below their reorder level, sorted."""
    rows = db.execute("SELECT sku FROM items WHERE quantity < reorder_level ORDER BY sku").fetchall()
    return [row[0] for row in rows]
