"""
Validators for AssetFlow Authentication Module
Handles email and password validation using regex patterns
"""

import re
from typing import Tuple


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email format using regex.
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email or not email.strip():
        return False, "Email is required"
    
    email = email.strip()
    
    # Email regex pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return False, "Invalid email format"
    
    return True, ""


def validate_full_name(full_name: str) -> Tuple[bool, str]:
    """
    Validate full name.
    
    Args:
        full_name: Full name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not full_name or not full_name.strip():
        return False, "Full name is required"
    
    full_name = full_name.strip()
    
    if len(full_name) < 2:
        return False, "Full name must be at least 2 characters"
    
    if len(full_name) > 100:
        return False, "Full name must not exceed 100 characters"
    
    return True, ""


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength.
    
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    # Check for uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    # Check for special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)"
    
    return True, ""


def validate_signup_input(full_name: str, email: str, password: str) -> Tuple[bool, str]:
    """
    Validate all signup inputs.
    
    Args:
        full_name: User's full name
        email: User's email address
        password: User's password
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate full name
    is_valid, error_msg = validate_full_name(full_name)
    if not is_valid:
        return False, error_msg
    
    # Validate email
    is_valid, error_msg = validate_email(email)
    if not is_valid:
        return False, error_msg
    
    # Validate password
    is_valid, error_msg = validate_password(password)
    if not is_valid:
        return False, error_msg
    
    return True, ""


def validate_login_input(email: str, password: str) -> Tuple[bool, str]:
    """
    Validate login inputs.
    
    Args:
        email: User's email address
        password: User's password
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email or not email.strip():
        return False, "Email is required"
    
    if not password:
        return False, "Password is required"
    
    return True, ""
