import sqlite3
import pandas as pd
from typing import List, Tuple, Optional
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'assetflow.db')

def get_connection() -> sqlite3.Connection:
    """Returns a connection to the SQLite database."""
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "assetflow.db")


def _get_connection():
    """Return a connection to the SQLite database."""
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
"""
Database module for AssetFlow
Handles SQLite database operations and initialization
"""

import sqlite3
import os
from typing import List, Dict, Tuple, Optional


class Database:
    """Database handler for AssetFlow"""
    
    def __init__(self, db_path: str = "assetflow.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get database connection.
        
        Returns:
            SQLite connection object
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database and create tables if they don't exist"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    full_name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            raise
    
    def user_exists_by_email(self, email: str) -> bool:
        """
        Check if user exists by email.
        
        Args:
            email: User's email address
            
        Returns:
            True if user exists, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT user_id FROM users WHERE email = ?', (email,))
            result = cursor.fetchone()
            conn.close()
            
            return result is not None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def create_user(self, user_id: str, full_name: str, email: str, 
                   password_hash: str, role: str = "employee", 
                   created_at: str = None) -> Tuple[bool, str]:
        """
        Create a new user.
        
        Args:
            user_id: Unique user identifier
            full_name: User's full name
            email: User's email address
            password_hash: Hashed password
            role: User role (employee or admin)
            created_at: Account creation timestamp
            
        Returns:
            Tuple of (success, message)
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if email already exists
            cursor.execute('SELECT user_id FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                conn.close()
                return False, "Email already registered"
            
            # Insert new user
            cursor.execute('''
                INSERT INTO users (user_id, full_name, email, password, role, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, full_name, email, password_hash, role, created_at))
            
            conn.commit()
            conn.close()
            
            return True, "User created successfully"
        except sqlite3.IntegrityError:
            return False, "Email already registered"
        except sqlite3.Error as e:
            return False, f"Database error: {e}"
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Get user by email.
        
        Args:
            email: User's email address
            
        Returns:
            User data dictionary or None
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, full_name, email, password, role, created_at 
                FROM users WHERE email = ?
            ''', (email,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return dict(result)
            return None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """
        Get user by user ID.
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            User data dictionary or None
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, full_name, email, password, role, created_at 
                FROM users WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return dict(result)
            return None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
    
    def get_all_users(self) -> List[Dict]:
        """
        Get all users.
        
        Returns:
            List of user data dictionaries
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, full_name, email, role, created_at 
                FROM users ORDER BY created_at DESC
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in results]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
    
    def get_user_count(self) -> int:
        """
        Get total number of users.
        
        Returns:
            Number of users
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) as count FROM users')
            result = cursor.fetchone()
            conn.close()
            
            return result['count'] if result else 0
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return 0
    
    def delete_user(self, user_id: str) -> Tuple[bool, str]:
        """
        Delete a user (admin only function).
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            Tuple of (success, message)
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
            conn.commit()
            conn.close()
            
            return True, "User deleted successfully"
        except sqlite3.Error as e:
            return False, f"Database error: {e}"
    
    def update_user_role(self, user_id: str, new_role: str) -> Tuple[bool, str]:
        """
        Update user role (admin only function).
        
        Args:
            user_id: User's unique identifier
            new_role: New role (admin or employee)
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if new_role not in ['admin', 'employee']:
                return False, "Invalid role. Must be 'admin' or 'employee'"
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('UPDATE users SET role = ? WHERE user_id = ?', 
                         (new_role, user_id))
            conn.commit()
            conn.close()
            
            return True, "Role updated successfully"
        except sqlite3.Error as e:
            return False, f"Database error: {e}"


# Initialize database on module import
db = Database()
