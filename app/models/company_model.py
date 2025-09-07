from app.db.database import Base, pk_int
from app.schemas.company_schema import CompanyRole
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, Index, Enum as SQLEnum, DateTime, UniqueConstraint, CheckConstraint, ARRAY, func, select
from typing import Optional, List
from datetime import datetime

class Company(Base):
    id: Mapped[pk_int]
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    website: Mapped[Optional[str]] =mapped_column(String(255), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False, unique=True)

    owner: Mapped['User'] = relationship('User', foreign_keys=[owner_id], back_populates='owner_company')
    members: Mapped[List['CompanyMember']] = relationship('CompanyMember', back_populates='company', cascade='all, delete-orphan')
    jobs: Mapped[List['Job']] = relationship('Job', back_populates='company', cascade='all, delete-orphan', lazy='select')
    invitations: Mapped[List['Invitations']] = relationship('Invitations', back_populates='company', cascade='all, delete-orphan')

    __table_args__ = (
        Index('idx_company_name', 'name'),
        Index('idx_company_owner', 'owner_id'),
        Index('idx_company_active', 'is_active'),
        Index('idx_company_industry', 'industry'),
        Index('idx_company_active_industry', 'is_active', 'industry')
    )

        
   
    def get_member_by_user_id(self, user_id: int) -> Optional['CompanyMember']:
        """Get company member by user ID"""
        return next((member for member in self.members if member.user_id == user_id and member.is_active), None)
    
    def can_user_create_jobs(self, user_id: int) -> bool:
        """Check if user can create jobs"""
        if self.owner_id == user_id:
            return True
        
        member = self.get_member_by_user_id(user_id)
        return member and (
            member.has_permission('CREATE_JOBS') or 
            member.has_permission('MANAGE_JOBS')
        )
    
    def can_user_edit_jobs(self, user_id: int) -> bool:
        """Check if user can edit jobs"""
        if self.owner_id == user_id:
            return True
        
        member = self.get_member_by_user_id(user_id)
        return member and (
            member.has_permission('EDIT_JOBS') or 
            member.has_permission('MANAGE_JOBS')
        )
    
    def can_user_delete_jobs(self, user_id: int) -> bool:
        """Check if user can delete jobs"""
        if self.owner_id == user_id:
            return True
        
        member = self.get_member_by_user_id(user_id)
        return member and (
            member.has_permission('DELETE_JOBS') or 
            member.has_permission('MANAGE_JOBS')
        )
    
    def can_user_view_applications(self, user_id: int) -> bool:
        """Check if user can view applications"""
        if self.owner_id == user_id:
            return True
        
        member = self.get_member_by_user_id(user_id)
        return member and (
            member.has_permission('VIEW_APPLICATIONS') or 
            member.has_permission('MANAGE_APPLICATIONS')
        )
    
    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name='{self.name}', active={self.is_active})>"
    

class Invitations(Base):
    id: Mapped[pk_int]
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    company_role: Mapped[CompanyRole] = mapped_column(SQLEnum(CompanyRole), nullable=False)
    token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'), nullable=False)
    invited_by: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    sender_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    opened_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    clicked_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    company: Mapped['Company'] = relationship('Company', back_populates='invitations')
    inviter: Mapped['User'] = relationship('User', foreign_keys=[invited_by])


    __table_args__ = (
        UniqueConstraint('email', 'company_id', 'is_used', name='uq_email_company_unused'),

        Index('idx_invitation_email', 'email'),
        Index('idx_invitation_token', 'token'),
        Index('idx_invitation_company', 'company_id'),
        Index('idx_invitation_expires', 'expires_at'),
        Index('idx_invitation_unused', 'is_used', 'expires_at'),
        Index('idx_invitation_sender_ip', 'sender_ip'),
        Index('idx_invitation_stats', 'opened_at', 'clicked_at'),

        CheckConstraint('expires_at > created_at', name='check_future_expiry_invitation'),
        CheckConstraint('char_length(trim(name)) >= 2', name='check_company_name_length'),
        CheckConstraint('website IS NULL OR website ~ \'^https?://\'', name='check_valid_website'),
    )

    @property
    def is_expired(self) -> bool:
        """Check if invitation has expired"""
        return datetime.utcnow() > self.expires_at

    @property
    def days_until_expiry(self) -> int:
        """Days until invitation expires"""
        if self.is_expired:
            return 0
        delta = self.expires_at - datetime.utcnow()
        return delta.days

    def can_be_used(self) -> bool:
        """Check if invitation can still be used"""
        return not self.is_used and not self.is_expired

    @classmethod
    def generate_token(cls) -> str:
        """Generate unique invitation token"""
        import secrets
        return secrets.token_urlsafe(32)

    def __repr__(self) -> str:
        return f"<Invitation(id={self.id}, email='{self.email}', company_id={self.company_id}, used={self.is_used})>"
    

class CompanyMember(Base):
    id: Mapped[pk_int]
    company_role: Mapped[CompanyRole] = mapped_column(SQLEnum(CompanyRole), nullable=False)
    permissions: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=[])
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="company_membership")

    __table_args__ = (
        # Unique constraint: one active membership per user per company
        UniqueConstraint('user_id', 'company_id', name='uq_user_company'),
        
        # Indexes
        Index('idx_member_company', 'company_id'),
        Index('idx_member_user', 'user_id'),
        Index('idx_member_active', 'is_active'),
        Index('idx_member_role', 'company_role'),
        Index('idx_member_permissions', 'permissions', postgresql_using='gin'),
        
        # Constraints
        CheckConstraint("company_role != 'owner'", name='check_no_owner_role'),  # Owner managed separately
    )

    def has_permission(self, permission: str) -> bool:
        """Check if member has specific permission"""
        return permission in (self.permissions or [])

    def add_permission(self, permission: str) -> bool:
        """Add permission if not exists"""
        if not self.permissions:
            self.permissions = []
        
        if permission not in self.permissions:
            self.permissions.append(permission)
            return True
        return False

    def remove_permission(self, permission: str) -> bool:
        """Remove permission if exists"""
        if self.permissions and permission in self.permissions:
            self.permissions.remove(permission)
            return True
        return False

    def get_permissions_list(self) -> list[str]:
        """Get all permissions as list"""
        return self.permissions or []

    @property
    def days_in_company(self) -> int:
        """Calculate days since joining company"""
        delta = datetime.utcnow() - self.joined_at
        return delta.days

    def __repr__(self) -> str:
        return f"<CompanyMember(id={self.id}, user_id={self.user_id}, company_id={self.company_id}, role='{self.company_role.value}')>"