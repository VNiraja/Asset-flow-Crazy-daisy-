"""
Authentication module for AssetFlow
Handles user authentication, password hashing, and session management
"""

import bcrypt
import uuid
from datetime import datetime
from typing import Tuple, Optional, Dict
from utils.db import db
from utils.validators import validate_signup_input, validate_login_input


class AuthManager:
    """Authentication manager for AssetFlow"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            password: Plain text password
            hashed_password: Hashed password from database
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            print(f"Password verification error: {e}")
            return False
    
    @staticmethod
    def generate_user_id() -> str:
        """
        Generate unique user ID using UUID.
        
        Returns:
            Unique user ID
        """
        return str(uuid.uuid4())
    
    @staticmethod
    def get_current_timestamp() -> str:
        """
        Get current timestamp in ISO format.
        
        Returns:
            Current timestamp
        """
        return datetime.now().isoformat()
    
    @staticmethod
    def signup(full_name: str, email: str, password: str, role: str = "employee") -> Tuple[bool, str]:
        """
        Register a new user.
        
        Args:
            full_name: User's full name
            email: User's email address
            password: User's password
            role: The user's role (admin or employee)
            
        Returns:
            Tuple of (success, message)
        """
        # Validate input
        is_valid, error_msg = validate_signup_input(full_name, email, password)
        if not is_valid:
            return False, error_msg
        
        # Check if email already exists
        if db.user_exists_by_email(email):
            return False, "Email already registered"
        
        try:
            # Generate user ID
            user_id = AuthManager.generate_user_id()
            
            # Hash password
            password_hash = AuthManager.hash_password(password)
            
            # Create user in database
            success, message = db.create_user(
                user_id=user_id,
                name=full_name,
                email=email,
                password_hash=password_hash,
                role=role
            )
            
            return success, message
        except Exception as e:
            return False, f"Signup error: {str(e)}"
    
    @staticmethod
    def login(email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Authenticate user login.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Tuple of (success, message, user_data)
        """
        # Validate input
        is_valid, error_msg = validate_login_input(email, password)
        if not is_valid:
            return False, error_msg, None
        
        try:
            # Get user from database
            user = db.get_user_by_email(email)
            
            if not user:
                return False, "Invalid email or password", None
            
            # Verify password
            if not AuthManager.verify_password(password, user['password']):
                return False, "Invalid email or password", None
            
            # Prepare user data for session
            user_session_data = {
                'user_id': user['user_id'],
                'username': user['full_name'],
                'email': user['email'],
                'role': user['role']
            }
            
            return True, "Login successful", user_session_data
        except Exception as e:
            return False, f"Login error: {str(e)}", None
    
    @staticmethod
    def get_user_info(user_id: str) -> Optional[Dict]:
        """
        Get user information.
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            User data dictionary or None
        """
        return db.get_user_by_id(user_id)
    
    @staticmethod
    def check_admin_access(user_role: str) -> bool:
        """
        Check if user has admin access.
        
        Args:
            user_role: User's role
            
        Returns:
            True if user is admin, False otherwise
        """
        return user_role == 'admin'


# Initialize auth manager
auth_manager = AuthManager()
