from app.db.database import Base, pk_int
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, Boolean, ForeignKey, ARRAY, DateTime, func, Enum as SQLEnum
from datetime import datetime
from app.schemas.company_schema import CompanyRole

class Company(Base):
    id: Mapped[pk_int]
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    industry: Mapped[str] = mapped_column(String(100), nullable=True)
    logo_url: Mapped[str] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('user.id'), unique=True)


class Invitations(Base):
    id: Mapped[pk_int]
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=False)
    company_role: Mapped[CompanyRole] = mapped_column(SQLEnum(CompanyRole), nullable=False)
    token: Mapped[str] = mapped_column(String(100), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'), nullable=False)
    invited_by: Mapped[int] = mapped_column(ForeignKey('user.id'))

 
class CompanyMember(Base):
    company_role: Mapped[CompanyRole] = mapped_column(SQLEnum(CompanyRole), nullable=False)
    permission: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
