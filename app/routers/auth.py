from fastapi import APIRouter
from app.services.auth_service import register_service
from app.schemas.user_schema import UserResponse, UserRequest, UserLogin


router = APIRouter(prefix='/auth', tags=['auth'])

@router.post('/register', response_model=UserResponse)
async def register(user: UserRequest):
    return await register_service(user)

