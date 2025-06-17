from passlib.context import CryptContext
from datetime import datetime, timedelta, UTC
from typing import Optional

from jose import jwt, JWTError

from src.config.settings import settings
from fastapi import HTTPException, status


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# !!!!!!! ДОДАЙТЕ ЦІ РЯДКИ ДЛЯ ОТЛАДКИ !!!!!!!
print(f"Loading settings from: {settings.__module__}")
print(f"Type of settings: {type(settings)}")
if hasattr(settings, 'ACCESS_TOKEN_EXPIRE_MINUTES'):
    print(f"ACCESS_TOKEN_EXPIRE_MINUTES found: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")
else:
    print("WARNING: ACCESS_TOKEN_EXPIRE_MINUTES NOT FOUND ON SETTINGS OBJECT!")
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


class PasswordHelper:
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Хешує пароль."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Перевіряє відповідність пароля хешу."""
        return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )