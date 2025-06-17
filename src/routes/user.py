# src/routes/users.py
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.database.setup import get_db
from src.schemas.user.user import UserResponse, UserUpdate
from src.services.user.user import UserService
from src.core.dependencies import get_current_user, role_required # Імпортуємо залежності для захисту
from src.models.user.user import User # Імпортуємо User та UserGroupEnum
from src.models.user.user_group import UserGroupEnum

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get(
    "/",
    response_model=List[UserResponse],
    summary="Get all users",
    description="Retrieves a list of all users. Requires admin privileges.",
    dependencies=[Depends(role_required([UserGroupEnum.ADMIN]))] # Тільки адмін може отримати всіх користувачів
)
async def get_all_users_endpoint(
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    return await user_service.get_all_users()


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Retrieves a single user by their ID. Requires admin privileges or being the user itself.",
    dependencies=[Depends(get_current_user)] # Використовуємо get_current_user для перевірки доступу
)
async def get_user_by_id_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) # Поточний автентифікований користувач
):
    user_service = UserService(db)
    # Дозволяємо доступ, якщо користувач адмін АБО якщо запитується його власний профіль
    if current_user.group.name == UserGroupEnum.ADMIN.value or current_user.id == user_id:
        return await user_service.get_user_by_id(user_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this user's profile"
        )


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update a user",
    description="Updates an existing user's information. Requires admin privileges or being the user itself.",
    dependencies=[Depends(get_current_user)] # Захищено, щоб тільки авторизовані могли оновлювати
)
async def update_user_endpoint(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_service = UserService(db)
    # Дозволяємо доступ, якщо користувач адмін АБО якщо він оновлює свій власний профіль
    if current_user.group.name == UserGroupEnum.ADMIN.value or current_user.id == user_id:
        return await user_service.update_user(user_id, user_data)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this user"
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
    description="Deletes a user by their ID. Requires admin privileges.",
    dependencies=[Depends(role_required([UserGroupEnum.ADMIN]))] # Тільки адмін може видаляти користувачів
)
async def delete_user_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    await user_service.delete_user(user_id)
    return {}