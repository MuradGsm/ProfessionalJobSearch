from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.utils.enums import UserRole
from app.models.users_model import User
from app.schemas.user_schema import (
    UserRequest, UserUpdate, UserResponse, UserProfile, 
    ChangePasswordRequest, UserSearchParams, UserStats,
    UserAdminUpdate, AccountSecurityInfo
)
from app.config.user_exceptions import (
    UserNotFoundError, EmailAlreadyExistsError, 
    InvalidCredentialsError, AccountLockedError,
    InvalidTokenError
)
from app.auth.hash import hash_password, verify_password
from app.utils.email import email_service
from app.utils.tokens import (
    generate_verification_token, generate_password_reset_token
)
from app.utils.validators import validate_password_strength, validate_name
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        pass

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Find user by email"""
        try:
            result = await db.execute(
                select(User)
                .options(
                    selectinload(User.company_membership),
                    selectinload(User.owned_company)
                )
                .where(and_(User.email == email.lower(), User.deleted_at.is_(None)))
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {str(e)}")
            raise

    async def create_user(self, db: AsyncSession, user_data: UserRequest) -> User:
        """Create new user account"""
        try:
            existing_user = await self.get_user_by_email(db, user_data.email)
            if existing_user:
                raise EmailAlreadyExistsError()

            validate_password_strength(user_data.password)
            cleaned_name = validate_name(user_data.name)

            user = User(
                name=cleaned_name,
                email=user_data.email.lower(),
                role=user_data.role,
                email_verification_token=generate_verification_token(),
            )
            user.set_password(user_data.password)

            db.add(user)
            await db.commit()
            await db.refresh(user)

            try:
                await email_service.send_verification_email(user.email, user.email_verification_token)
                await email_service.send_welcome_email(user.email, user.name)
            except Exception as email_error:
                logger.warning(f"Failed to send emails for user {user.email}: {str(email_error)}")

            logger.info(f"Created new user: {user.email} with role {user.role}")
            return user   # 👈 возвращаем ORM-модель

        except EmailAlreadyExistsError:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create user {user_data.email}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account"
            )

    async def authenticate_user(self, db: AsyncSession, email: str, password: str, ip_address: str = None) -> User:
        """Authenticate user and handle login attempts"""
        try:
            user = await self.get_user_by_email(db, email.lower())
            if not user:
                raise InvalidCredentialsError()

            if user.is_locked():
                raise AccountLockedError(
                    f"Account locked until {user.locked_until.strftime('%Y-%m-%d %H:%M:%S')}"
                )

            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is deactivated"
                )

            if not user.verify_password(password):
                user.increment_failed_login(ip_address)
                if user.login_attempts >= 5:
                    user.lock_account(30)
                    await db.commit()
                    raise AccountLockedError("Account locked due to multiple failed login attempts")
                await db.commit()
                raise InvalidCredentialsError()

            # Successful login
            user.login_attempts = 0
            user.failed_login_ips = []
            user.update_last_login()
            await db.commit()

            return user

        except (InvalidCredentialsError, AccountLockedError, HTTPException):
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Unexpected authentication error for {email}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication failed"
            )
        
    async def verify_email(self, db: AsyncSession, token: str):
        user = await db.execute(select(User).where(User.email_verification_token == token))
        user = user.scalar_one_or_none()
        if not user:
            raise InvalidTokenError("Invalid email verification token")
        
        user.email_verified = True
        user.email_verification_token = None
        db.add(user)
        await db.commit()

user_service = UserService()
