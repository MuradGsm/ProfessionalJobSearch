from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.auth.deps import get_current_user
from app.models.users_model import User
from app.services.users_service import user_service

router = APIRouter()

@router.delete("/delete", status_code=204)
async def delete_my_account(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    await user_service.delete_user_service(db, current_user)
    return {"message": "Account successfully deleted"}