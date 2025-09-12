from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict, ValidationInfo
from app.utils.enums import UserRole
from typing import Optional
from datetime import datetime

# ===== USER REGISTRATION & LOGIN =====
class UserRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    role: UserRole = Field(..., description="Choose role", json_schema_extra={"example": "candidate"})
    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Token expiration time in seconds")
    user: "UserResponse" = Field(description="User information")

# ===== USER RESPONSE & PROFILE =====
class UserResponse(BaseModel):
    id: int
    name: str
    role: UserRole 
    email: EmailStr
    is_admin: bool = False
    is_active: bool = True
    email_verified: bool = False
    company_id: Optional[int] = None
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 

class UserProfile(BaseModel):
    """Extended user profile information"""
    id: int
    name: str
    email: EmailStr
    role: UserRole
    is_admin: bool
    is_active: bool
    email_verified: bool
    two_factor_enabled: bool
    company_id: Optional[int] = None
    company_name: Optional[str] = None
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Statistics
    total_applications: int = 0
    total_resumes: int = 0
    unread_notifications: int = 0
    unread_messages: int = 0

    model_config = ConfigDict(from_attributes=True)

# ===== USER UPDATES =====
class UserUpdate(BaseModel):
    """Update user profile information"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None

    @field_validator('name')
    def validate_name(cls, v):
        if v and not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip() if v else v

class ChangePasswordRequest(BaseModel):
    """Change user password"""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

    @field_validator('new_password')
    def validate_new_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

    @field_validator('confirm_password')
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        if info.data.get('new_password') and v != info.data.get('new_password'):
            raise ValueError('Passwords do not match')
        return v


# ===== PASSWORD RESET =====
class PasswordResetRequest(BaseModel):
    """Request password reset via email"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Confirm password reset with token"""
    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

    @field_validator('new_password')
    def validate_new_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

    @field_validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

# ===== EMAIL VERIFICATION =====
class EmailVerificationRequest(BaseModel):
    """Request email verification"""
    email: EmailStr

class EmailVerificationConfirm(BaseModel):
    """Confirm email verification with token"""
    token: str = Field(..., min_length=1)

# ===== USER SEARCH & FILTERS =====
class UserSearchParams(BaseModel):
    """Search and filter parameters for users"""
    name: Optional[str] = Field(None, min_length=1)
    email: Optional[str] = Field(None, min_length=1)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = Field(default=True)
    is_admin: Optional[bool] = None
    email_verified: Optional[bool] = None
    has_company: Optional[bool] = None
    
    # Date filters
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    last_login_after: Optional[datetime] = None
    
    # Sorting
    sort_by: Optional[str] = Field(default="created_at", pattern="^(created_at|name|email|last_login)$")
    sort_order: Optional[str] = Field(default="desc", pattern="^(asc|desc)$")
    
    # Pagination
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

# ===== ADMIN OPERATIONS =====
class UserAdminUpdate(BaseModel):
    """Admin-only user updates"""
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    email_verified: Optional[bool] = None
    role: Optional[UserRole] = None
    unlock_account: Optional[bool] = None
    force_password_change: Optional[bool] = None

# ===== BULK OPERATIONS =====
class BulkUserAction(BaseModel):
    """Bulk operations on users"""
    user_ids: list[int] = Field(..., min_length=1, max_length=100)
    action: str = Field(..., pattern="^(activate|deactivate|delete|verify_email)$")

# ===== USER STATISTICS =====
class UserStats(BaseModel):
    """User statistics"""
    total_users: int
    active_users: int
    verified_users: int
    candidates_count: int
    employers_count: int
    admins_count: int
    users_with_companies: int
    locked_accounts: int
    recent_registrations: int 
    recent_logins: int  

# ===== ACCOUNT SECURITY =====
class AccountSecurityInfo(BaseModel):
    """Account security information"""
    two_factor_enabled: bool
    last_password_change: Optional[datetime]
    recent_failed_attempts: int
    is_locked: bool
    locked_until: Optional[datetime]
    backup_codes_count: int = 0
    should_force_password_change: bool = False

class Enable2FARequest(BaseModel):
    """Enable 2FA request"""
    password: str = Field(..., min_length=1)

class Verify2FARequest(BaseModel):
    """Verify 2FA token"""
    token: str = Field(..., min_length=6, max_length=6)
    backup_code: Optional[str] = Field(None, min_length=8, max_length=12)

TokenResponse.model_rebuild()