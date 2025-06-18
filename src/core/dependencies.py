from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.database.setup import get_db
from src.core.security import decode_token
from src.models.user.user import User
from src.models.user.user_group import UserGroupEnum
from src.services.user.user import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> User:
    payload = decode_token(token)

    user_id = payload.get("user_id")
    username = payload.get("sub")

    if user_id is None or username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_service = UserService(db)
    current_user = await user_service.get_user_by_id(user_id)

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


def role_required(allowed_roles: List[UserGroupEnum]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.group.name not in [role.value for role in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required roles: {[role.value for role in allowed_roles]}"
            )
        return current_user

    return role_checker
