# src/dependencies/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.database.setup import get_db
from src.core.security import decode_token
from src.models.user.user import User
from src.models.user.user_group import UserGroupEnum
from src.schemas.user.token import TokenData
from src.services.user.user import UserService

# OAuth2PasswordBearer - це інструмент FastAPI для роботи з токенами
# tokenUrl вказує, куди клієнт має відправити логін/пароль для отримання токена.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")  # Вказуємо шлях до ендпоінта логіну


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> User:
    """Залежність, що повертає поточного автентифікованого користувача."""
    payload = decode_token(token)  # Використовуємо нашу утиліту для декодування

    user_id = payload.get("user_id")
    username = payload.get("sub")  # 'sub' зазвичай зберігає ім'я користувача

    if user_id is None or username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Використовуємо UserService для отримання користувача
    user_service = UserService(db)
    current_user = await user_service.get_user_by_id(user_id)  # Завантажуємо користувача з БД

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found in database",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


# Залежність для перевірки ролей (додамо її пізніше)
def role_required(allowed_roles: List[UserGroupEnum]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.group.name not in [role.value for role in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required roles: {[role.value for role in allowed_roles]}"
            )
        return current_user

    return role_checker