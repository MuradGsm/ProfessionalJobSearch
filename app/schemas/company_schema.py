from pydantic import BaseModel, EmailStr, Field, field_validator
from enum import Enum
from datetime import datetime
from typing import List, Optional

# ===== ENUMS =====
class CompanyRole(str, Enum):
    OWNER = "owner"
    RECRUITER = "recruiter"
    HR_MANAGER = "hr_manager"

class CompanyPermission(str, Enum):
    MANAGE_JOBS = "manage_jobs"
    CREATE_JOBS = "create_jobs"
    EDIT_JOBS = "edit_jobs"
    DELETE_JOBS = "delete_jobs"
    VIEW_APPLICATIONS = "view_applications"
    MANAGE_APPLICATIONS = "manage_applications"
    INVITE_MEMBERS = "invite_members"
    MANAGE_MEMBERS = "manage_members"

# ===== COMPANY SCHEMAS =====
class CompanyBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200, description="Company name")
    description: str = Field(..., min_length=10, max_length=1000, description="Company description")
    industry: Optional[str] = Field(None, max_length=100, description="Company industry")
    website: Optional[str] = Field(None, max_length=255, description="Company website")
    logo_url: Optional[str] = Field(None, max_length=500, description="Company logo URL")

    @field_validator('website')
    def validate_website(cls, v):
        if v and not (v.startswith('http://') or v.startswith('https://')):
            return f"https://{v}"
        return v

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=1000)
    industry: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=255)
    logo_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

class CompanyResponse(CompanyBase):
    id: int
    owner_id: int
    is_active: bool
    total_members_count: int = Field(description="Total active members including owner")
    active_jobs_count: int = Field(description="Count of active jobs")
    pending_invitations_count: int = Field(description="Count of pending invitations")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== INVITATION SCHEMAS =====
class InvitationCreate(BaseModel):
    email: EmailStr = Field(..., description="Email to invite")
    company_role: CompanyRole = Field(..., description="Role for invited user")
    permissions: List[CompanyPermission] = Field(default_factory=list, description="Permissions to grant")

    @field_validator('permissions')
    def validate_permissions_for_role(cls, v, values):
        role = values.get('company_role')
        
        # Default permissions based on role
        if role == CompanyRole.RECRUITER:
            default_permissions = [
                CompanyPermission.CREATE_JOBS,
                CompanyPermission.EDIT_JOBS,
                CompanyPermission.VIEW_APPLICATIONS
            ]
        elif role == CompanyRole.HR_MANAGER:
            default_permissions = [
                CompanyPermission.VIEW_APPLICATIONS,
                CompanyPermission.MANAGE_APPLICATIONS,
                CompanyPermission.CREATE_JOBS
            ]
        else:
            default_permissions = []
        
        # If no permissions specified, use defaults
        if not v:
            return default_permissions
        
        # Validate permissions are appropriate for role
        if role == CompanyRole.RECRUITER and CompanyPermission.MANAGE_MEMBERS in v:
            raise ValueError('Recruiters cannot have member management permissions')
        
        return v

class InvitationResponse(BaseModel):
    id: int
    email: str
    company_role: CompanyRole
    company_id: int
    invited_by: int
    is_used: bool
    is_expired: bool = Field(description="Whether invitation has expired")
    days_until_expiry: int = Field(description="Days until expiry")
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True

class InvitationAccept(BaseModel):
    token: str = Field(..., description="Invitation token")
    user_id: int = Field(..., description="User accepting the invitation")

# ===== COMPANY MEMBER SCHEMAS =====
class CompanyMemberBase(BaseModel):
    company_role: CompanyRole = Field(..., description="Role in company")
    permissions: List[CompanyPermission] = Field(default_factory=list, description="Granted permissions")

class CompanyMemberUpdate(BaseModel):
    company_role: Optional[CompanyRole] = None
    permissions: Optional[List[CompanyPermission]] = None
    is_active: Optional[bool] = None

class CompanyMemberResponse(CompanyMemberBase):
    id: int
    user_id: int
    company_id: int
    is_active: bool
    joined_at: datetime
    days_in_company: int = Field(description="Days since joining company")
    
    user_name: Optional[str] = None
    user_email: Optional[str] = None

    class Config:
        from_attributes = True

# ===== COMPANY SEARCH/FILTER SCHEMAS =====
class CompanySearchParams(BaseModel):
    name: Optional[str] = Field(None, min_length=1, description="Search by company name")
    industry: Optional[str] = Field(None, min_length=1, description="Filter by industry")
    is_active: Optional[bool] = Field(default=True, description="Filter by active status")
    has_jobs: Optional[bool] = Field(None, description="Filter companies with active jobs")
    
    # Sorting
    sort_by: Optional[str] = Field(default="created_at", pattern="^(created_at|name|active_jobs_count)$")
    sort_order: Optional[str] = Field(default="desc", pattern="^(asc|desc)$")
    
    # Pagination
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=50)

# ===== STATISTICS SCHEMAS =====
class CompanyStats(BaseModel):
    total_companies: int
    active_companies: int
    companies_with_jobs: int
    avg_jobs_per_company: float
    avg_members_per_company: float
    companies_by_industry: dict

class CompanyDashboard(BaseModel):
    company_info: CompanyResponse
    recent_jobs: List[dict] = Field(description="Recent 5 jobs")
    pending_applications: int = Field(description="Total pending applications")
    team_members: List[CompanyMemberResponse] = Field(description="All team members")
    pending_invitations: List[InvitationResponse] = Field(description="Pending invitations")
    stats: dict = Field(description="Company performance stats")