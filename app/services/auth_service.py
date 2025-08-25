from fastapi import HTTPException, status, Depends
from app.schemas.user_schema import UserResponse,UserRequest, UserLogin
from app.db.fake_db import users_db
from app.auth.hash import hash_password

async def register_service(user_data: UserRequest) -> UserResponse:
    for user in users_db:
        if user.email == user_data.email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already exists')
    new_id = len(users_db)+1
    new_user = UserResponse(
        id=new_id,
        name=user_data.name,
        role=user_data.role,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)      
    )
    users_db.append(new_user)
    return new_user



