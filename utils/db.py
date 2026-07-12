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
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL
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
    
    def create_user(self, user_id: str, name: str, email: str, 
                   password_hash: str, role: str = "employee") -> Tuple[bool, str]:
        """
        Create a new user.
        
        Args:
            user_id: Unique user identifier
            name: User's name
            email: User's email address
            password_hash: Hashed password
            role: User role (employee or admin)
            
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
                INSERT INTO users (user_id, name, email, password, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, name, email, password_hash, role))
            
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
                SELECT user_id, name as full_name, email, password, role 
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
                SELECT user_id, name as full_name, email, password, role 
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
                SELECT user_id, name as full_name, email, role 
                FROM users
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
