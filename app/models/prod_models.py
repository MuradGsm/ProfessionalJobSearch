from app.db.database import Base, pk_int
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, JSON, ForeignKey, Index, Float
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
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    request_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    __table_args__ = (
        Index('idx_audit_table_action', 'table_name', 'action'),
        Index('idx_audit_user_action', 'user_id', 'action', 'created_at'),
        Index('idx_audit_ip', 'ip_address'),
        Index('idx_audit_session', 'session_id'),
        Index('idx_audit_record', 'table_name', 'record_id'),
    )

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

class PerformanceMetric(Base):
    id: Mapped[pk_int]
    endpoint: Mapped[str] = mapped_column(String(100), nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    response_time: Mapped[float] = mapped_column(Float, nullable=False)  
    status_code: Mapped[int] = mapped_column(nullable=False) 
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey('user.id'), nullable=True) 
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True) 

    __table_args__ = ( 
        Index('idx_perf_endpoint', 'endpoint', 'created_at'),
        Index('idx_perf_response_time', 'response_time'),
        Index('idx_perf_status', 'status_code'),
        Index('idx_perf_user', 'user_id'),
    )

class CacheEntry(Base):
    id: Mapped[pk_int] 
    key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    value: Mapped[dict] = mapped_column(JSON, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    hit_count: Mapped[int] = mapped_column(default=0)
    
    __table_args__ = (
        Index('idx_cache_expires', 'expires_at'),
        Index('idx_cache_key', 'key'),
    )

class SchemaVersion(Base):
    id: Mapped[pk_int]
    version: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    applied_by: Mapped[str] = mapped_column(String(100), nullable=False)
    
    __table_args__ = (
        Index('idx_schema_version', 'version'),
        Index('idx_schema_applied_by', 'applied_by'),
    )