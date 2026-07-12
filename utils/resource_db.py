"""
resource_db.py - Asset, Allocation, and Maintenance database functions for AssetFlow.
Uses the shared assetflow.db SQLite database.
"""

import sqlite3
import pandas as pd
from typing import List, Tuple, Optional
import os
import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "assetflow.db")


def _get_connection() -> sqlite3.Connection:
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    """Create Assets, Allocations, and Maintenance tables if they don't exist."""
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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Allocations (
                allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id      INTEGER NOT NULL,
                employee_name TEXT    NOT NULL,
                assigned_date TEXT    NOT NULL,
                returned_date TEXT,
                status        TEXT    NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Maintenance (
                maintenance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id       INTEGER NOT NULL,
                maintenance_date TEXT  NOT NULL,
                description    TEXT    NOT NULL,
                cost           REAL    NOT NULL,
                status         TEXT    NOT NULL
            )
        """)


# ---------------------------------------------------------------------------
# Asset CRUD
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Allocation functions
# ---------------------------------------------------------------------------

def get_available_assets():
    """Return all assets that are currently Available."""
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM Assets WHERE status = 'Available' ORDER BY asset_id"
        ).fetchall()
    return [dict(row) for row in rows]


def get_allocated_assets():
    """Return all currently assigned allocations."""
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM Allocations WHERE status = 'Assigned' ORDER BY assigned_date DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def assign_asset(asset_id: int, employee_name: str, assigned_date: str) -> bool:
    """Assign an asset to an employee and mark it as Assigned."""
    with _get_connection() as conn:
        conn.execute(
            "INSERT INTO Allocations (asset_id, employee_name, assigned_date, status) VALUES (?, ?, ?, 'Assigned')",
            (asset_id, employee_name, assigned_date)
        )
        conn.execute("UPDATE Assets SET status = 'Assigned' WHERE asset_id = ?", (asset_id,))
    return True


def return_asset(allocation_id: int, returned_date: str) -> bool:
    """Mark an allocation as returned and set asset back to Available."""
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT asset_id FROM Allocations WHERE allocation_id = ?", (allocation_id,)
        ).fetchone()
        if not row:
            return False
        conn.execute(
            "UPDATE Allocations SET returned_date = ?, status = 'Returned' WHERE allocation_id = ?",
            (returned_date, allocation_id)
        )
        conn.execute("UPDATE Assets SET status = 'Available' WHERE asset_id = ?", (row["asset_id"],))
    return True


def get_allocation_history() -> pd.DataFrame:
    """Get complete allocation history."""
    with _get_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM Allocations ORDER BY assigned_date DESC", conn)
    return df


def search_allocations(asset_id: Optional[int], employee_name: str) -> pd.DataFrame:
    """Search allocation history by asset_id and/or employee_name."""
    query  = "SELECT * FROM Allocations WHERE 1=1"
    params = []
    if asset_id:
        query += " AND asset_id = ?"
        params.append(asset_id)
    if employee_name:
        query += " AND employee_name LIKE ?"
        params.append(f"%{employee_name}%")
    query += " ORDER BY assigned_date DESC"
    with _get_connection() as conn:
        df = pd.read_sql_query(query, conn, params=params)
    return df


# ---------------------------------------------------------------------------
# Maintenance functions
# ---------------------------------------------------------------------------

def add_maintenance(asset_id: int, maintenance_date: str, description: str, cost: float, status: str) -> bool:
    """Add a new maintenance record and update the asset's status."""
    with _get_connection() as conn:
        conn.execute(
            "INSERT INTO Maintenance (asset_id, maintenance_date, description, cost, status) VALUES (?, ?, ?, ?, ?)",
            (asset_id, maintenance_date, description, cost, status)
        )
        new_asset_status = "Maintenance" if status == "In Progress" else "Available"
        conn.execute("UPDATE Assets SET status = ? WHERE asset_id = ?", (new_asset_status, asset_id))
    return True


def get_maintenance_history() -> pd.DataFrame:
    """Get complete maintenance history."""
    with _get_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM Maintenance ORDER BY maintenance_date DESC", conn)
    return df


def search_maintenance(asset_id: Optional[int], status: str) -> pd.DataFrame:
    """Search maintenance history."""
    query  = "SELECT * FROM Maintenance WHERE 1=1"
    params = []
    if asset_id:
        query += " AND asset_id = ?"
        params.append(asset_id)
    if status and status != "All":
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY maintenance_date DESC"
    with _get_connection() as conn:
        df = pd.read_sql_query(query, conn, params=params)
    return df


# ---------------------------------------------------------------------------
# Asset Lifecycle Intelligence
# ---------------------------------------------------------------------------

def compute_asset_risk(asset: dict) -> dict:
    """Compute a simple risk profile for an asset based on age and status."""
    score = 0
    today = datetime.date.today()

    # Age scoring
    try:
        purchase_date = datetime.date.fromisoformat(str(asset.get("purchase_date", "")))
        age_years = (today - purchase_date).days / 365.25
    except (ValueError, TypeError):
        age_years = 0

    if age_years > 5:
        score += 40
        lifecycle_stage = "End of Life"
    elif age_years > 3:
        score += 20
        lifecycle_stage = "Mature"
    elif age_years > 1:
        score += 10
        lifecycle_stage = "Active"
    else:
        lifecycle_stage = "New"

    # Status scoring
    status = asset.get("status", "")
    if status == "Maintenance":
        score += 40
    elif status == "Assigned":
        score += 10

    # Missing data penalty
    if not asset.get("location"):
        score += 10

    score = min(score, 100)

    if score >= 70:
        risk_level = "High Risk"
        recommendation = "Schedule immediate inspection or replacement."
    elif score >= 40:
        risk_level = "Medium Risk"
        recommendation = "Plan maintenance within the next 30 days."
    else:
        risk_level = "Low Risk"
        recommendation = "No immediate action required."

    return {
        "score": score,
        "risk_level": risk_level,
        "age_years": round(age_years, 1),
        "lifecycle_stage": lifecycle_stage,
        "recommendation": recommendation,
    }


# Initialize tables when module is imported
create_tables()
