from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users_model import User
from sqlalchemy import select
from app.schemas.user_schema import UserRequest
from app.auth.hash import hash_password, verify_password
from app.auth.jwt import create_access_token, create_refresh_token

async def register_service(user_data: UserRequest, session: AsyncSession) -> User:
    result = await session.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()
    if user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already exists')
    new_user = User(
        name=user_data.name,
        role=user_data.role,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)      
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


async def login_service(session: AsyncSession, form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    result = await  session.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    if user is not None and verify_password(form_data.password, user.hashed_password):
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
