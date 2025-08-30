from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.services.auth_service import register_service, login_service
from app.schemas.user_schema import UserResponse, UserRequest, TokenResponse

router = APIRouter(prefix='/auth', tags=['auth'])

@router.post('/register', response_model=UserResponse)
async def register(user: UserRequest, session: AsyncSession = Depends(get_session)):
    return await register_service(user, session)

@router.post('/login', response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    return await login_service(session, form_data)