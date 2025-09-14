from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.schemas.user_schema import EmailVerificationRequest, EmailVerificationConfirm
from app.services.users_service import user_service
from app.config.user_exceptions import InvalidTokenError

router = APIRouter()

@router.get("/verify", summary="Verify user email via link")
async def verify_email_get(token: str, db: AsyncSession = Depends(get_session)):
    try:
        await user_service.verify_email(db, token)
        return {"message": "Email verified successfully"}
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/resend", summary="Resend email verification link")
async def resend_verification(
    data: EmailVerificationRequest,
    db: AsyncSession = Depends(get_session)
):
    try:
        await user_service.resend_verification_email(db, data.email)
        return {"message": "If the email exists, a verification link has been sent"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resend verification email: {str(e)}"
        )
