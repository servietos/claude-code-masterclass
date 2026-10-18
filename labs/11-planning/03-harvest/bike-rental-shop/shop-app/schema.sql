CREATE TABLE IF NOT EXISTS bikes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT NOT NULL UNIQUE,
    frame_size TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'available',
    last_service_date TEXT
);

CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT
);

CREATE TABLE IF NOT EXISTS rentals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bike_id INTEGER NOT NULL REFERENCES bikes(id),
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    rented_at TEXT NOT NULL,
    due_at TEXT NOT NULL,
    returned_at TEXT,
    deposit_cents INTEGER,
    late_fee_cents INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS maintenance_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bike_id INTEGER NOT NULL REFERENCES bikes(id),
    note TEXT NOT NULL,
    logged_at TEXT NOT NULL
);
