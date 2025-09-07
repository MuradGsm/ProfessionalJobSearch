from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.prod_models import AuditLog
import json
import logging

logger = logging.getLogger(__name__)

class AuditService:
    """Service for logging audit events"""
    
    @staticmethod
    async def log_action(
        db: AsyncSession,
        table_name: str,
        record_id: int,
        action: str,
        user_id: Optional[int] = None,
        old_values: Optional[Dict[Any, Any]] = None,
        new_values: Optional[Dict[Any, Any]] = None,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """Log an audit action"""
        try:
            audit_log = AuditLog(
                table_name=table_name,
                record_id=record_id,
                action=action,
                old_values=old_values,
                new_values=new_values,
                user_id=user_id,
                ip_address=ip_address,
                session_id=session_id,
                user_agent=user_agent,
                request_id=request_id
            )
            
            db.add(audit_log)
            await db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log audit action: {str(e)}")
            await db.rollback()

    @staticmethod
    async def log_user_action(
        db: AsyncSession,
        user_id: int,
        action: str,
        details: Optional[Dict[Any, Any]] = None,
        ip_address: Optional[str] = None
    ):
        """Log a user-specific action"""
        await AuditService.log_action(
            db=db,
            table_name="user",
            record_id=user_id,
            action=action,
            user_id=user_id,
            new_values=details,
            ip_address=ip_address
        )

audit_service = AuditService()
