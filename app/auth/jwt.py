from fastapi import HTTPException
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.config.setting import settings as setting

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "sub": str(data.get("sub"))})
    return jwt.encode(to_encode, setting.JWT_SECRET_KEY, algorithm=setting.JWT_ALGORITHM)

def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(token, setting.JWT_SECRET_KEY, algorithms=[setting.JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise ValueError("Token payload missing user_id")
        return int(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "sub": str(data.get("sub"))})
    return jwt.encode(to_encode, setting.JWT_SECRET_KEY, algorithm=setting.JWT_ALGORITHM)

def decode_refresh_token(token: str) -> int:
    try:
        payload = jwt.decode(token, setting.JWT_SECRET_KEY, algorithms=[setting.JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise ValueError("Token payload missing user_id")
        return int(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
