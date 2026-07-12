import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "assetflow.db")


def _get_connection():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    """Create the Assets table if it does not already exist."""
    with _get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Assets (
                asset_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_name    TEXT    NOT NULL,
                category      TEXT    NOT NULL,
                purchase_date TEXT,
                purchase_cost REAL,
                location      TEXT,
                status        TEXT
            )
        """)


def add_asset(asset_name, category, purchase_date, purchase_cost, location, status):
    """Insert a new asset record and return the new asset_id."""
    with _get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO Assets (asset_name, category, purchase_date, purchase_cost, location, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (asset_name, category, purchase_date, purchase_cost, location, status),
        )
        return cursor.lastrowid


def get_all_assets():
    """Return all asset records as a list of dicts."""
    with _get_connection() as conn:
        rows = conn.execute("SELECT * FROM Assets ORDER BY asset_id DESC").fetchall()
    return [dict(row) for row in rows]


def search_assets(name: str = "", category: str = "All", status: str = "All"):
    """Return filtered assets based on name substring, category, and status."""
    query  = "SELECT * FROM Assets WHERE asset_name LIKE ?"
    params = [f"%{name}%"]

    if category != "All":
        query += " AND category = ?"
        params.append(category)

    if status != "All":
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY asset_id DESC"

    with _get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def get_asset_by_id(asset_id: int):
    """Return a single asset record as a dict, or None if not found."""
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM Assets WHERE asset_id = ?", (asset_id,)
        ).fetchone()
    return dict(row) if row else None


def update_asset(asset_id, asset_name, category, purchase_date, purchase_cost, location, status):
    """Update all fields of an existing asset by asset_id."""
    with _get_connection() as conn:
        conn.execute(
            """
            UPDATE Assets
               SET asset_name    = ?,
                   category      = ?,
                   purchase_date = ?,
                   purchase_cost = ?,
                   location      = ?,
                   status        = ?
             WHERE asset_id = ?
            """,
            (asset_name, category, purchase_date, purchase_cost, location, status, asset_id),
        )


def delete_asset(asset_id: int):
    """Permanently delete an asset record by asset_id."""
    with _get_connection() as conn:
        conn.execute("DELETE FROM Assets WHERE asset_id = ?", (asset_id,))
