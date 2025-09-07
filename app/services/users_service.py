from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.users_model import User, UserRole
from app.schemas.user_schema import (
    UserRequest, UserUpdate, UserResponse, UserProfile, 
    ChangePasswordRequest, UserSearchParams, UserStats,
    BulkUserAction, UserAdminUpdate, AccountSecurityInfo
)
from app.config.user_exceptions import (
    UserNotFoundError, EmailAlreadyExistsError, 
    InvalidCredentialsError, AccountLockedError,
    EmailNotVerifiedError, InvalidTokenError
)
from app.auth.hash import hash_password, verify_password
from app.utils.email import email_service
from app.utils.tokens import (
    generate_verification_token, generate_password_reset_token,
    generate_2fa_backup_codes
)
from app.utils.validators import validate_password_strength, validate_name
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        pass

    async def create_user(self, db: AsyncSession, user_data: UserRequest) -> User:
        """Create new user account"""
        # Check if email already exists
        existing_user = await self.get_user_by_email(db, user_data.email)
        if existing_user:
            raise EmailAlreadyExistsError()

        # Validate password
        validate_password_strength(user_data.password)
        
        # Validate and clean name
        cleaned_name = validate_name(user_data.name)

        # Create new user
        user = User(
            name=cleaned_name,
            email=user_data.email.lower(),
            role=user_data.role,
            email_verification_token=generate_verification_token()
        )
        user.set_password(user_data.password)

        db.add(user)
        try:
            await db.commit()
            await db.refresh(user)
            
            # Send verification email (async)
            await email_service.send_verification_email(
                user.email, user.email_verification_token
            )
            
            # Send welcome email
            await email_service.send_welcome_email(user.email, user.name)
            
            logger.info(f"Created new user: {user.email} with role {user.role}")
            return user
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create user {user_data.email}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account"
            )

    async def authenticate_user(self, db: AsyncSession, email: str, password: str, ip_address: str = None) -> User:
        """Authenticate user and handle login attempts"""
        user = await self.get_user_by_email(db, email.lower())
        if not user:
            raise InvalidCredentialsError()

        # Check if account is locked
        if user.is_locked():
            raise AccountLockedError(
                f"Account locked until {user.locked_until.strftime('%Y-%m-%d %H:%M:%S')}"
            )

        # Check if account is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )

        # Verify password
        if not user.verify_password(password):
            # Increment failed attempts
            user.increment_failed_login(ip_address)
            
            # Lock account after 5 failed attempts
            if user.login_attempts >= 5:
                user.lock_account(30)  # Lock for 30 minutes
                await db.commit()
                raise AccountLockedError("Account locked due to multiple failed login attempts")
            
            await db.commit()
            raise InvalidCredentialsError()

        # Successful login
        user.update_last_login()
        await db.commit()
        
        logger.info(f"User {user.email} logged in successfully")
        return user

    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID with relationships"""
        result = await db.execute(
            select(User)
            .options(
                selectinload(User.company_membership),
                selectinload(User.owned_company)
            )
            .where(and_(User.id == user_id, User.deleted_at.is_(None)))
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(
            select(User)
            .where(and_(User.email == email.lower(), User.deleted_at.is_(None)))
        )
        return result.scalar_one_or_none()

    async def get_user_profile(self, db: AsyncSession, user_id: int) -> UserProfile:
        """Get detailed user profile with statistics"""
        user = await self.get_user_by_id(db, user_id)
        if not user:
            raise UserNotFoundError()

        # Get statistics
        stats_query = await db.execute(
            select(
                func.count(User.applications).label('total_applications'),
                func.count(User.resumes).label('total_resumes'),
                func.count(User.notifications.and_(User.notifications.c.is_read == False)).label('unread_notifications'),
                func.count(User.received_messages.and_(User.received_messages.c.is_read == False)).label('unread_messages')
            )
            .where(User.id == user_id)
        )
        stats = stats_query.first()

        return UserProfile(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            is_admin=user.is_admin,
            is_active=user.is_active,
            email_verified=user.email_verified,
            two_factor_enabled=user.two_factor_enabled,
            company_id=user.get_company_id(),
            company_name=user.owned_company.name if user.owned_company else (
                user.company_membership.company.name if user.company_membership else None
            ),
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at,
            total_applications=stats.total_applications or 0,
            total_resumes=stats.total_resumes or 0,
            unread_notifications=stats.unread_notifications or 0,
            unread_messages=stats.unread_messages or 0
        )

    async def update_user(self, db: AsyncSession, user_id: int, user_data: UserUpdate) -> User:
        """Update user profile"""
        user = await self.get_user_by_id(db, user_id)
        if not user:
            raise UserNotFoundError()

        update_fields = {}
        
        if user_data.name is not None:
            update_fields['name'] = validate_name(user_data.name)
        
        if user_data.email is not None:
            # Check if new email already exists
            if user_data.email.lower() != user.email:
                existing_user = await self.get_user_by_email(db, user_data.email)
                if existing_user:
                    raise EmailAlreadyExistsError()
                
                update_fields['email'] = user_data.email.lower()
                update_fields['email_verified'] = False
                update_fields['email_verification_token'] = generate_verification_token()

        if update_fields:
            update_fields['updated_at'] = datetime.utcnow()
            await db.execute(
                update(User).where(User.id == user_id).values(**update_fields)
            )
            await db.commit()
            await db.refresh(user)

        return user

    async def change_password(self, db: AsyncSession, user_id: int, password_data: ChangePasswordRequest) -> bool:
        """Change user password"""
        user = await self.get_user_by_id(db, user_id)
        if not user:
            raise UserNotFoundError()

        # Verify current password
        if not user.verify_password(password_data.current_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Validate new password
        validate_password_strength(password_data.new_password)
        
        # Update password
        user.set_password(password_data.new_password)
        await db.commit()

        logger.info(f"Password changed for user {user.email}")
        return True

    async def request_password_reset(self, db: AsyncSession, email: str) -> bool:
        """Request password reset via email"""
        user = await self.get_user_by_email(db, email)
        if not user:
            # Don't reveal if email exists or not
            return True

        # Generate reset token
        reset_token = generate_password_reset_token()
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        
        await db.commit()

        # Send reset email
        await email_service.send_password_reset_email(user.email, reset_token)
        return True

    async def confirm_password_reset(self, db: AsyncSession, token: str, new_password: str) -> bool:
        """Confirm password reset with token"""
        user_result = await db.execute(
            select(User).where(
                and_(
                    User.password_reset_token == token,
                    User.password_reset_expires > datetime.utcnow(),
                    User.deleted_at.is_(None)
                )
            )
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise InvalidTokenError()

        # Validate new password
        validate_password_strength(new_password)
        
        # Update password and clear reset token
        user.set_password(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        user.unlock_account()  # Unlock if locked
        
        await db.commit()
        
        logger.info(f"Password reset completed for user {user.email}")
        return True

    async def verify_email(self, db: AsyncSession, token: str) -> bool:
        """Verify user email with token"""
        user_result = await db.execute(
            select(User).where(
                and_(
                    User.email_verification_token == token,
                    User.deleted_at.is_(None)
                )
            )
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise InvalidTokenError()

        user.email_verified = True
        user.email_verification_token = None
        await db.commit()
        
        logger.info(f"Email verified for user {user.email}")
        return True

    async def search_users(self, db: AsyncSession, params: UserSearchParams) -> tuple[List[UserResponse], int]:
        """Search users with filters and pagination"""
        query = select(User).where(User.deleted_at.is_(None))
        
        # Apply filters
        if params.name:
            query = query.where(User.name.ilike(f"%{params.name}%"))
        
        if params.email:
            query = query.where(User.email.ilike(f"%{params.email}%"))
        
        if params.role:
            query = query.where(User.role == params.role)
        
        if params.is_active is not None:
            query = query.where(User.is_active == params.is_active)
        
        if params.is_admin is not None:
            query = query.where(User.is_admin == params.is_admin)
        
        if params.email_verified is not None:
            query = query.where(User.email_verified == params.email_verified)
        
        if params.created_after:
            query = query.where(User.created_at >= params.created_after)
        
        if params.created_before:
            query = query.where(User.created_at <= params.created_before)

        # Count total
        count_query = select(func.count(User.id)).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply sorting
        sort_column = getattr(User, params.sort_by)
        if params.sort_order == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        offset = (params.page - 1) * params.page_size
        query = query.offset(offset).limit(params.page_size)

        result = await db.execute(query)
        users = result.scalars().all()

        user_responses = [
            UserResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                role=user.role,
                is_admin=user.is_admin,
                is_active=user.is_active,
                email_verified=user.email_verified,
                company_id=user.get_company_id(),
                last_login=user.last_login,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            for user in users
        ]

        return user_responses, total

    async def get_user_stats(self, db: AsyncSession) -> UserStats:
        """Get user statistics"""
        stats_query = await db.execute(
            select(
                func.count(User.id).label('total_users'),
                func.count(User.id).filter(User.is_active == True).label('active_users'),
                func.count(User.id).filter(User.email_verified == True).label('verified_users'),
                func.count(User.id).filter(User.role == UserRole.candidate).label('candidates_count'),
                func.count(User.id).filter(User.role == UserRole.employer).label('employers_count'),
                func.count(User.id).filter(User.is_admin == True).label('admins_count'),
                func.count(User.id).filter(User.locked_until > datetime.utcnow()).label('locked_accounts'),
                func.count(User.id).filter(User.created_at >= datetime.utcnow() - timedelta(days=30)).label('recent_registrations'),
                func.count(User.id).filter(User.last_login >= datetime.utcnow() - timedelta(hours=24)).label('recent_logins')
            )
            .where(User.deleted_at.is_(None))
        )
        
        stats = stats_query.first()
        
        # Count users with companies
        company_users_query = await db.execute(
            select(func.count(User.id.distinct()))
            .outerjoin(User.owned_company)
            .outerjoin(User.company_membership)
            .where(
                and_(
                    User.deleted_at.is_(None),
                    or_(
                        User.owned_company.has(),
                        User.company_membership.has()
                    )
                )
            )
        )
        users_with_companies = company_users_query.scalar()

        return UserStats(
            total_users=stats.total_users,
            active_users=stats.active_users,
            verified_users=stats.verified_users,
            candidates_count=stats.candidates_count,
            employers_count=stats.employers_count,
            admins_count=stats.admins_count,
            users_with_companies=users_with_companies,
            locked_accounts=stats.locked_accounts,
            recent_registrations=stats.recent_registrations,
            recent_logins=stats.recent_logins
        )

    async def admin_update_user(self, db: AsyncSession, user_id: int, admin_data: UserAdminUpdate) -> User:
        """Admin-only user updates"""
        user = await self.get_user_by_id(db, user_id)
        if not user:
            raise UserNotFoundError()

        update_fields = {}
        
        if admin_data.is_active is not None:
            update_fields['is_active'] = admin_data.is_active
        
        if admin_data.is_admin is not None:
            update_fields['is_admin'] = admin_data.is_admin
        
        if admin_data.email_verified is not None:
            update_fields['email_verified'] = admin_data.email_verified
            if admin_data.email_verified:
                update_fields['email_verification_token'] = None
        
        if admin_data.role is not None:
            update_fields['role'] = admin_data.role
        
        if admin_data.unlock_account:
            user.unlock_account()
        
        if admin_data.force_password_change:
            update_fields['last_password_change'] = datetime.utcnow() - timedelta(days=91)

        if update_fields:
            update_fields['updated_at'] = datetime.utcnow()
            await db.execute(
                update(User).where(User.id == user_id).values(**update_fields)
            )
            await db.commit()
            await db.refresh(user)

        return user

    async def delete_user(self, db: AsyncSession, user_id: int, soft_delete: bool = True) -> bool:
        """Delete user (soft delete by default)"""
        user = await self.get_user_by_id(db, user_id)
        if not user:
            raise UserNotFoundError()

        if soft_delete:
            # Soft delete
            await db.execute(
                update(User)
                .where(User.id == user_id)
                .values(
                    deleted_at=datetime.utcnow(),
                    is_active=False,
                    email=f"deleted_{user_id}_{user.email}"  # Prevent email conflicts
                )
            )
        else:
            # Hard delete
            await db.execute(delete(User).where(User.id == user_id))

        await db.commit()
        logger.info(f"User {user.email} {'soft' if soft_delete else 'hard'} deleted")
        return True

    async def get_account_security_info(self, db: AsyncSession, user_id: int) -> AccountSecurityInfo:
        """Get account security information"""
        user = await self.get_user_by_id(db, user_id)
        if not user:
            raise UserNotFoundError()

        return AccountSecurityInfo(
            two_factor_enabled=user.two_factor_enabled,
            last_password_change=user.last_password_change,
            recent_failed_attempts=user.login_attempts,
            is_locked=user.is_locked(),
            locked_until=user.locked_until,
            backup_codes_count=len(user.backup_codes) if user.backup_codes else 0,
            should_force_password_change=user.should_force_password_change()
        )

# Global service instance
user_service = UserService()