from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user_schema import UserResponse
from app.auth.jwt import decode_access_token
from app.db.database import get_session
from app.services.users_service import user_service
from app.config.user_exceptions import UserNotFoundError
import logging
from typing import Optional

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_session)
) -> UserResponse:
    """Get current authenticated user"""
    try:
        # Decode JWT token to get user_id
        user_id = decode_access_token(token)
        
        # Get user from database
        user = await user_service.get_user_by_id(db, user_id)
        if not user:
            raise UserNotFoundError("User not found")
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )
        
        # Return user response
        return UserResponse(
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
        
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token'
        )

async def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user

async def get_current_verified_user(
    current_user: UserResponse = Depends(get_current_active_user)
) -> UserResponse:
    """Get current verified user"""
    if not current_user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )
    return current_user

async def admin_required(
    current_user: UserResponse = Depends(get_current_active_user)
) -> UserResponse:
    """Require admin privileges"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Admin access required'
        )
    return current_user

async def candidate_required(
    current_user: UserResponse = Depends(get_current_active_user)
) -> UserResponse:
    """Require candidate role"""
    if current_user.role != 'candidate':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Candidate access required'
        )
    return current_user

async def employer_required(
    current_user: UserResponse = Depends(get_current_active_user)
) -> UserResponse:
    """Require employer role"""
    if current_user.role != 'employer':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Employer access required'
        )
    return current_user

async def get_optional_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_session)
) -> Optional[UserResponse]:
    """Get current user if authenticated, None otherwise"""
    try:
        return await get_current_user(token, db)
    except:
        return None

# IP address helper
async def get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    # Check for forwarded IP first (in case of proxy/load balancer)
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    
    # Check for real IP header
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    # Fall back to direct client host
    return request.client.host if request.client else "unknown"
