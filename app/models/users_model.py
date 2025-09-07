from app.db.database import Base, pk_int  
from app.auth.hash import hash_password, verify_password
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, String, Enum as SQLEnum, Index, ForeignKey, ARRAY
from enum import Enum as PyEnum
from typing import Optional
from datetime import datetime, timedelta

class UserRole(str, PyEnum):
    candidate = "candidate"
    employer = "employer"

class User(Base):
    id: Mapped[pk_int]
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole, name="userrole"), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Security fields
    email_verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password_reset_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password_reset_expires: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    backup_codes: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)

    # Activity tracking
    last_login: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    login_attempts: Mapped[int] = mapped_column(default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    last_password_change: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    failed_login_ips: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String(45)), nullable=True)

    # Relationships
    resumes: Mapped[list["Resume"]] = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    applications: Mapped[list["Application"]] = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    sent_messages: Mapped[list["Message"]] = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender", cascade="all, delete-orphan", lazy="dynamic")
    received_messages: Mapped[list["Message"]] = relationship("Message", foreign_keys="Message.recipient_id", back_populates="recipient", cascade="all, delete-orphan")
    company_membership: Mapped[Optional["CompanyMember"]] = relationship("CompanyMember", back_populates="user")
    owned_company: Mapped[Optional["Company"]] = relationship("Company", foreign_keys="Company.owner_id", back_populates="owner")

    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_role', 'role'),
        Index('idx_user_active', 'is_active'),
        Index('idx_user_email_verified', 'email', 'email_verified'),
        Index('idx_user_deleted', 'deleted_at'),
        Index('idx_user_locked', 'locked_until'),
        Index('idx_user_last_login', 'last_login'),
        Index('idx_user_verification_token', 'email_verification_token'),
        Index('idx_user_reset_token', 'password_reset_token'),
    )

    def set_password(self, password: str):
        """Set hashed password and update last_password_change"""
        self.hashed_password = hash_password(password)
        self.last_password_change = datetime.utcnow()
    
    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash"""
        return verify_password(password, self.hashed_password)
    
    def is_locked(self) -> bool:
        """Check if account is currently locked"""
        return bool(self.locked_until and self.locked_until > datetime.utcnow())
    
    def lock_account(self, minutes: int = 30):
        """Lock account for specified minutes"""
        self.locked_until = datetime.utcnow() + timedelta(minutes=minutes)
    
    def unlock_account(self):
        """Unlock account and reset login attempts"""
        self.locked_until = None
        self.login_attempts = 0
        self.failed_login_ips = []

    def increment_failed_login(self, ip_address: str = None):
        """Increment failed login attempts and track IP"""
        self.login_attempts += 1
        if ip_address:
            if not self.failed_login_ips:
                self.failed_login_ips = []
            if ip_address not in self.failed_login_ips:
                self.failed_login_ips.append(ip_address)

    def should_force_password_change(self, days: int = 90) -> bool:
        """Check if user should be forced to change password"""
        if not self.last_password_change:
            return True
        return (datetime.utcnow() - self.last_password_change).days > days

    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        self.login_attempts = 0 

    def get_company_id(self) -> Optional[int]:
        """Get user's company ID"""
        if self.owned_company:
            return self.owned_company.id
        if self.company_membership and self.company_membership.is_active:
            return self.company_membership.company_id
        return None

    def can_create_company(self) -> bool:
        """Check if user can create a company"""
        return self.role == UserRole.employer and not self.owned_company and not self.company_membership

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"