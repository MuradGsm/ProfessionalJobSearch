from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.db.database import get_session
from app.config.setting import settings
from app.schemas.user_schema import (
    UserRequest, UserResponse, TokenResponse, UserLogin,
    PasswordResetRequest, PasswordResetConfirm,
    EmailVerificationRequest, EmailVerificationConfirm
)
from app.services.users_service import user_service
from app.auth.jwt import create_access_token, create_refresh_token
from app.auth.deps import get_client_ip, get_current_user
from app.utils.audit import audit_service
from app.config.user_exceptions import (
    EmailAlreadyExistsError, InvalidCredentialsError,
    AccountLockedError, InvalidTokenError
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRequest,
    request: Request,
    db: AsyncSession = Depends(get_session)
):
    """Register new user"""
    try:
        ip_address = await get_client_ip(request)
        user = await user_service.create_user(db, user_data)
        
        # Log registration
        await audit_service.log_user_action(
            db=db,
            user_id=user.id,
            action="register",
            details={"role": user.role.value},
            ip_address=ip_address
        )
        
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            is_admin=user.is_admin,
            is_active=user.is_active,
            email_verified=user.email_verified,
            company_id=user.get_company_id(),
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except EmailAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

@router.post("/login", response_model=TokenResponse)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: AsyncSession = Depends(get_session)
):
    """Login user and return JWT tokens"""
    try:
        ip_address = await get_client_ip(request) if request else None
        
        # Authenticate user
        user = await user_service.authenticate_user(
            db, form_data.username, form_data.password, ip_address
        )
        
        # Create tokens
        access_token = create_access_token({"sub": user.id})
        refresh_token = create_refresh_token({"sub": user.id})
        
        # Log successful login
        await audit_service.log_user_action(
            db=db,
            user_id=user.id,
            action="login",
            ip_address=ip_address
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(
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
        )
        
    except (InvalidCredentialsError, AccountLockedError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.post("/request-password-reset")
async def request_password_reset(
    request_data: PasswordResetRequest,
    db: AsyncSession = Depends(get_session)
):
    """Request password reset via email"""
    await user_service.request_password_reset(db, request_data.email)
    return {"message": "If the email exists, a password reset link has been sent"}

@router.post("/confirm-password-reset")
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_session)
):
    """Confirm password reset with token"""
    try:
        await user_service.confirm_password_reset(
            db, reset_data.token, reset_data.new_password
        )
        return {"message": "Password reset successful"}
        
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/verify-email")
async def verify_email(
    verification_data: EmailVerificationConfirm,
    db: AsyncSession = Depends(get_session)
):
    """Verify user email with token"""
    try:
        await user_service.verify_email(db, verification_data.token)
        return {"message": "Email verified successfully"}
        
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/resend-verification")
async def resend_email_verification(
    request_data: EmailVerificationRequest,
    db: AsyncSession = Depends(get_session)
):
    """Resend email verification"""
    # This would need implementation in user_service
    return {"message": "If the email exists, a verification link has been sent"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_user)
):
    """Get current user information"""
    return current_user

@router.post("/logout")
async def logout_user(
    request: Request,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Logout user (for logging purposes)"""
    ip_address = await get_client_ip(request)
    
    # Log logout
    await audit_service.log_user_action(
        db=db,
        user_id=current_user.id,
        action="logout",
        ip_address=ip_address
    )
    
    return {"message": "Logged out successfully"}