from app.db.database import Base, pk_int
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, JSON, ForeignKey, Index
from typing import Optional
from datetime import datetime

class AuditLog(Base):
    id: Mapped[pk_int]
    table_name: Mapped[str] = mapped_column(String(50), nullable=False)
    record_id: Mapped[int] = mapped_column(nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    old_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    new_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey('user.id'), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)


class RateLimit(Base):
    id: Mapped[pk_int]
    identifier: Mapped[str] = mapped_column(String(100), nullable=False) 
    endpoint: Mapped[str] = mapped_column(String(100), nullable=False)
    count: Mapped[int] = mapped_column(default=1)
    window_start: Mapped[datetime] = mapped_column(nullable=False)
    
    __table_args__ = (
        Index('idx_rate_limit_identifier', 'identifier', 'endpoint'),
        Index('idx_rate_limit_window', 'window_start'),
    )
