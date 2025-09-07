import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional

def generate_secure_token(length: int = 32) -> str:
    """Generate cryptographically secure token"""
    return secrets.token_urlsafe(length)

def generate_verification_token() -> str:
    """Generate email verification token"""
    return generate_secure_token(32)

def generate_password_reset_token() -> str:
    """Generate password reset token"""
    return generate_secure_token(24)

def generate_2fa_backup_codes(count: int = 10) -> list[str]:
    """Generate 2FA backup codes"""
    codes = []
    for _ in range(count):
        code = secrets.token_hex(6).upper()
        # Format as XXXX-XXXX
        formatted_code = f"{code[:4]}-{code[4:8]}"
        codes.append(formatted_code)
    return codes

def hash_token(token: str) -> str:
    """Hash token for secure storage"""
    return hashlib.sha256(token.encode()).hexdigest()

def verify_token_hash(token: str, token_hash: str) -> bool:
    """Verify token against its hash"""
    return hash_token(token) == token_hash
