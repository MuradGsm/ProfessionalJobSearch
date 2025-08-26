from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user_schema import UserResponse,UserRequest
from app.db.fake_db import users_db
from app.auth.hash import hash_password, verify_password
from app.auth.jwt import create_access_token, create_refresh_token

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


async def login_service(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    for user in users_db:
        if user.email == form_data.username:  # ⚠️ username == email
            if verify_password(form_data.password, user.hashed_password):
                access_token = create_access_token(data={"sub": str(user.id)})
                refresh_token = create_refresh_token(data={"sub": str(user.id)})

                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer"
                }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password"
    )
