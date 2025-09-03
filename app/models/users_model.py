from app.db.database import Base, pk_int
from app.auth.hash import hash_password, verify_password
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, String, Enum as SQLEnum, Index, ForeignKey
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

    email_verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password_reset_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password_reset_expires: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    last_login: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    login_attempts: Mapped[int] = mapped_column(default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships
    resumes: Mapped[list["Resume"]] = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    applications: Mapped[list["Application"]] = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    sent_messages: Mapped[list["Message"]] = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender", cascade="all, delete-orphan")
    received_messages: Mapped[list["Message"]] = relationship("Message", foreign_keys="Message.recipient_id", back_populates="recipient", cascade="all, delete-orphan")
    company_membership: Mapped[Optional["CompanyMember"]] = relationship("CompanyMember", back_populates="user")
    owner_company: Mapped[Optional["Company"]] = relationship("Company", foreign_keys="Company.owner_id", back_populates="owner")

    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_role', 'role'),
        Index('idx_user_active', 'is_active'),
        Index('idx_user_email_verifed', 'email', 'email_verified'),
        Index('idx_user_deleted', 'deleted_at'),
        Index('idx_user_locked', 'locked_until')
    )

    def set_password(self, password: str):
        self.hashed_password = hash_password(password)
    
    def verify_password(self, password: str) -> bool:
        return verify_password(password, self.hashed_password)
    
    def is_locked(self) -> bool:
        return bool(self.locked_until and self.locked_until > datetime.utcnow())
    
    def lock_account(self, minutes: int = 30):
        self.locked_until = datetime.utcnow() + timedelta(minutes=minutes)
    
    def unlock_account(self):
        self.locked_until = None
        self.login_attempts = 0

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"