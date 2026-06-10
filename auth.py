"""
Authentication module for Streamlit app - handles login, signup, and user management
"""

import hashlib
import json
from pathlib import Path
from datetime import datetime

USERS_FILE = Path("users_data.json")

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load user data from JSON file"""
    if USERS_FILE.exists():
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users: dict):
    """Save user data to JSON file"""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def user_exists(username: str) -> bool:
    """Check if user already exists"""
    users = load_users()
    return username.lower() in users

def register_user(username: str, email: str, password: str) -> tuple[bool, str]:
    """
    Register a new user
    Returns: (success, message)
    """
    if not username or not email or not password:
        return False, "All fields are required"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    if user_exists(username):
        return False, "Username already exists"
    
    users = load_users()
    users[username.lower()] = {
        "email": email,
        "password": hash_password(password),
        "created_at": datetime.now().isoformat(),
        "fund_house": "All",  # Default filter
    }
    save_users(users)
    return True, "Account created successfully! Please login."

def verify_login(username: str, password: str) -> tuple[bool, str]:
    """
    Verify login credentials
    Returns: (success, message)
    """
    users = load_users()
    
    if not username or not password:
        return False, "Please enter username and password"
    
    if username.lower() not in users:
        return False, "Invalid username or password"
    
    user = users[username.lower()]
    if user["password"] != hash_password(password):
        return False, "Invalid username or password"
    
    return True, "Login successful"

def get_user_info(username: str) -> dict:
    """Get user information"""
    users = load_users()
    return users.get(username.lower(), {})

def update_user_filter(username: str, fund_house: str):
    """Update user's default fund house filter"""
    users = load_users()
    if username.lower() in users:
        users[username.lower()]["fund_house"] = fund_house
        save_users(users)
