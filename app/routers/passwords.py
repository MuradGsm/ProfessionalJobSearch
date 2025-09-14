from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.services.users_service import user_service
from app.config.user_exceptions import InvalidTokenError
from app.schemas.user_schema import PasswordResetConfirm

router = APIRouter()

@router.post("/request-password-reset", summary="Send password reset link")
async def request_password_reset(email: str, db: AsyncSession = Depends(get_session)):
    try:
        await user_service.reset_password_service(db, email)
        return {"message": "If the email exists, a reset link has been sent"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send password reset email: {str(e)}"
        )


@router.post("/confirm-password-reset", summary="Confirm password reset with token")
async def confirm_password_reset(
    data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_session)
):
    try:
        await user_service.confirm_password_reset(db, data.token, data.new_password)
        return {"message": "Password has been reset successfully"}
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )