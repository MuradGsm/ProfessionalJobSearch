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
from app.utils import dto
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
        
        return dto.map_user_to_response(user)
    except EmailAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session)):
    """Standard login endpoint"""
    try:
        user = await user_service.authenticate_user(
            db=db,
            email=form_data.username,  
            password=form_data.password,
            ip_address="127.0.0.1"  # Get from request in production
        )
        
        access_token = create_access_token({"sub": user.id, "role": user.role.value})
        refresh_token = create_refresh_token({"sub": user.id})

        return {
    "access_token": access_token,
    "refresh_token": refresh_token,
    "token_type": "bearer",
    "user": {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role.value if hasattr(user.role, 'value') else str(user.role)
    }
}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

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