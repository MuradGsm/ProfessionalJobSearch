import secrets
import string
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status

class SecurityUtils:
    """Security utilities"""
    
    @staticmethod
    def generate_session_id() -> str:
        """Generate secure session ID"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_csrf_token() -> str:
        """Generate CSRF token"""
        return secrets.token_urlsafe(24)
    
    @staticmethod
    def is_password_compromised(password: str) -> bool:
        """Check if password is in common password lists (simplified)"""
        common_passwords = [
            "password", "123456", "password123", "admin", "qwerty",
            "letmein", "welcome", "monkey", "1234567890", "dragon"
        ]
        return password.lower() in common_passwords
    
    @staticmethod
    def check_rate_limit(attempts: int, window_minutes: int, max_attempts: int) -> bool:
        """Simple rate limiting check"""
        return attempts < max_attempts
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove path separators and dangerous characters
        safe_chars = string.ascii_letters + string.digits + ".-_"
        sanitized = "".join(c for c in filename if c in safe_chars)
        
        # Limit length
        if len(sanitized) > 100:
            name, ext = sanitized.rsplit(".", 1) if "." in sanitized else (sanitized, "")
            sanitized = name[:95] + ("." + ext if ext else "")
        
        return sanitized or "file"
    
    @staticmethod
    def validate_file_type(filename: str, allowed_types: list[str]) -> bool:
        """Validate file type by extension"""
        if not filename or "." not in filename:
            return False
        
        ext = filename.lower().split(".")[-1]
        return ext in [t.lower() for t in allowed_types]

security_utils = SecurityUtils()