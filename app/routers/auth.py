from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth_service import register_service, login_service
from app.schemas.user_schema import UserResponse, UserRequest


router = APIRouter(prefix='/auth', tags=['auth'])

@router.post('/register', response_model=UserResponse)
async def register(user: UserRequest):
    return await register_service(user)

@router.post('/login')
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await login_service(form_data)