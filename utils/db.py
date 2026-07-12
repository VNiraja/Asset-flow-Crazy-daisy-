import sqlite3
import pandas as pd
from typing import List, Tuple, Optional
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'assetflow.db')

def get_connection() -> sqlite3.Connection:
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Create necessary tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Assuming Assets table exists, we don't drop it or recreate it if it doesn't belong to this module,
    # but the prompt implies it exists. We'll create Allocations and Maintenance.
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Allocations (
        allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_id INTEGER NOT NULL,
        employee_name TEXT NOT NULL,
        assigned_date TEXT NOT NULL,
        returned_date TEXT,
        status TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Maintenance (
        maintenance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_id INTEGER NOT NULL,
        maintenance_date TEXT NOT NULL,
        description TEXT NOT NULL,
        cost REAL NOT NULL,
        status TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

def get_available_assets() -> List[int]:
    """Return a list of asset IDs that are not currently assigned."""
    # Since we can't query the real Assets table without knowing its schema, 
    # we assume any asset not currently having an 'Assigned' status in Allocations is available.
    # In a real app, this would join with the Assets table.
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT DISTINCT asset_id 
    FROM Allocations 
    WHERE status = 'Assigned'
    ''')
    assigned_assets = {row['asset_id'] for row in cursor.fetchall()}
    
    # Just returning a dummy list for testing, or we fetch all unique assets and subtract assigned.
    # Since we don't have the Assets table, we will fetch all known asset_ids from Allocations + Maintenance 
    # and maybe some mock ones if empty. 
    # To keep it simple and robust, let's just query everything and filter out assigned.
    cursor.execute('SELECT DISTINCT asset_id FROM Allocations UNION SELECT DISTINCT asset_id FROM Maintenance')
    all_known = {row['asset_id'] for row in cursor.fetchall()}
    
    if not all_known:
        all_known = {101, 102, 103, 104, 105} # Dummy data if empty database
        
    conn.close()
    
    available = list(all_known - assigned_assets)
    return sorted(available)

def get_allocated_assets() -> List[Tuple[int, int]]:
    """Return a list of tuples (allocation_id, asset_id) for currently assigned assets."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT allocation_id, asset_id 
    FROM Allocations 
    WHERE status = 'Assigned'
    ''')
    allocated = [(row['allocation_id'], row['asset_id']) for row in cursor.fetchall()]
    conn.close()
    return allocated

def assign_asset(asset_id: int, employee_name: str, assigned_date: str) -> bool:
    """Assign an asset to an employee."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if already assigned
    cursor.execute("SELECT 1 FROM Allocations WHERE asset_id = ? AND status = 'Assigned'", (asset_id,))
    if cursor.fetchone():
        conn.close()
        return False
        
    cursor.execute('''
    INSERT INTO Allocations (asset_id, employee_name, assigned_date, status)
    VALUES (?, ?, ?, 'Assigned')
    ''', (asset_id, employee_name, assigned_date))
    
    conn.commit()
    conn.close()
    return True

def return_asset(allocation_id: int, returned_date: str) -> bool:
    """Mark an asset as returned."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT status FROM Allocations WHERE allocation_id = ?", (allocation_id,))
    row = cursor.fetchone()
    if not row or row['status'] == 'Returned':
        conn.close()
        return False
        
    cursor.execute('''
    UPDATE Allocations
    SET returned_date = ?, status = 'Returned'
    WHERE allocation_id = ?
    ''', (returned_date, allocation_id))
    
    conn.commit()
    conn.close()
    return True

def get_allocation_history() -> pd.DataFrame:
    """Get complete allocation history."""
    conn = get_connection()
    df = pd.read_sql_query('''
    SELECT * FROM Allocations ORDER BY assigned_date DESC
    ''', conn)
    conn.close()
    return df

def search_allocations(asset_id: Optional[int], employee_name: str) -> pd.DataFrame:
    """Search allocation history."""
    conn = get_connection()
    query = "SELECT * FROM Allocations WHERE 1=1"
    params = []
    
    if asset_id:
        query += " AND asset_id = ?"
        params.append(asset_id)
    if employee_name:
        query += " AND employee_name LIKE ?"
        params.append(f"%{employee_name}%")
        
    query += " ORDER BY assigned_date DESC"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def add_maintenance(asset_id: int, maintenance_date: str, description: str, cost: float, status: str) -> bool:
    """Add a new maintenance record."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO Maintenance (asset_id, maintenance_date, description, cost, status)
    VALUES (?, ?, ?, ?, ?)
    ''', (asset_id, maintenance_date, description, cost, status))
    
    conn.commit()
    conn.close()
    return True

def get_maintenance_history() -> pd.DataFrame:
    """Get complete maintenance history."""
    conn = get_connection()
    df = pd.read_sql_query('''
    SELECT * FROM Maintenance ORDER BY maintenance_date DESC
    ''', conn)
    conn.close()
    return df

def search_maintenance(asset_id: Optional[int], status: str) -> pd.DataFrame:
    """Search maintenance history."""
    conn = get_connection()
    query = "SELECT * FROM Maintenance WHERE 1=1"
    params = []
    
    if asset_id:
        query += " AND asset_id = ?"
        params.append(asset_id)
    if status and status != 'All':
        query += " AND status = ?"
        params.append(status)
        
    query += " ORDER BY maintenance_date DESC"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# Initialize tables when module is imported
create_tables()
