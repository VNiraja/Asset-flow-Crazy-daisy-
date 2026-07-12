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


def compute_asset_risk(asset: dict) -> dict:
    """
    Compute an Asset Risk Score (0-100) for a single asset dict.

    Score is derived from three independent components:
      - Age score      (0-40 pts)  based on years since purchase_date
      - Status score   (0-40 pts)  based on current operational status
      - Data score     (0-20 pts)  based on completeness of key fields

    A HIGHER score means HIGHER risk.
    Classification: Low Risk (0-39) | Medium Risk (40-69) | High Risk (70-100)

    No database queries are made — works entirely on the dict passed in.
    """
    import datetime

    # ── Age component (higher age = higher risk) ──────────────────────────────
    age_years = 0
    try:
        purchase = datetime.date.fromisoformat(asset["purchase_date"])
        age_years = (datetime.date.today() - purchase).days / 365.25
    except (TypeError, ValueError):
        age_years = 0  # unknown date treated as new

    if age_years < 2:
        age_score = 0       # new asset, no age risk
    elif age_years < 4:
        age_score = 15      # moderate age
    elif age_years < 6:
        age_score = 28      # aging
    else:
        age_score = 40      # old asset, maximum age risk

    # ── Status component ──────────────────────────────────────────────────────
    status_map = {
        "Available":   0,   # operational, no risk
        "Assigned":    15,  # in use, minor risk
        "Maintenance": 40,  # under repair, maximum status risk
    }
    status_score = status_map.get(asset.get("status", ""), 20)

    # ── Data completeness component (missing data = higher uncertainty = risk) ─
    incomplete_fields = sum([
        not asset.get("purchase_date"),
        not asset.get("purchase_cost"),
        not asset.get("location"),
    ])
    data_score = incomplete_fields * 7   # max 21, capped at 20
    data_score = min(data_score, 20)

    # ── Final score ───────────────────────────────────────────────────────────
    score = min(age_score + status_score + data_score, 100)

    # ── Classification ────────────────────────────────────────────────────────
    if score < 40:
        risk_level = "Low Risk"
    elif score < 70:
        risk_level = "Medium Risk"
    else:
        risk_level = "High Risk"

    # ── Lifecycle stage label ─────────────────────────────────────────────────
    if age_years < 2:
        lifecycle_stage = "New"
    elif age_years < 4:
        lifecycle_stage = "Active"
    elif age_years < 6:
        lifecycle_stage = "Aging"
    else:
        lifecycle_stage = "End of Life"

    # ── Recommendation ────────────────────────────────────────────────────────
    status = asset.get("status", "")
    name   = asset.get("asset_name", "This asset")
    age_label = f"{age_years:.1f} years" if age_years > 0 else "unknown age"

    if status == "Maintenance":
        recommendation = (
            f"{name} is currently under maintenance. "
            "Review repair status and estimate return-to-service date."
        )
    elif lifecycle_stage == "End of Life":
        recommendation = (
            f"{name} has been active for {age_label}. "
            "Consider replacement or formal decommission review."
        )
    elif lifecycle_stage == "Aging":
        recommendation = (
            f"{name} is aging ({age_label}). "
            "Schedule a maintenance review to assess condition."
        )
    elif lifecycle_stage == "Active" and status == "Assigned":
        recommendation = (
            f"{name} is in active use ({age_label}). "
            "Monitor utilisation and plan next service cycle."
        )
    else:
        recommendation = (
            f"{name} is relatively new and available. "
            "Continue normal usage."
        )

    return {
        "score":           score,
        "risk_level":      risk_level,
        "lifecycle_stage": lifecycle_stage,
        "age_years":       round(age_years, 1),
        "recommendation":  recommendation,
    }
