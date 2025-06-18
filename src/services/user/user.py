from typing import List
from datetime import datetime, UTC

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.user.user import User
from src.models.user.user_group import UserGroup
from src.schemas.user.user import UserUpdate, UserUpdateGroup
from src.core.security import PasswordHelper


class UserService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_all_users(self) -> List[User]:
        result = await self.db_session.execute(
            select(User).options(selectinload(User.group))
        )
        return result.scalars().all()

    async def get_user_by_id(self, user_id: int) -> User:
        user = await self.db_session.execute(
            select(User).options(selectinload(User.group)).where(User.id == user_id)
        )
        user = user.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    async def get_user_by_username(self, username: str) -> User:
        user = await self.db_session.execute(
            select(User).options(selectinload(User.group)).where(User.username == username)
        )
        user = user.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        user = await self.db_session.execute(
            select(User).options(selectinload(User.group)).where(User.id == user_id)
        )
        user = user.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        update_data = user_data.model_dump(exclude_unset=True)

        if "password" in update_data and update_data["password"]:
            user.password_hash = PasswordHelper.get_password_hash(update_data["password"])
            del update_data["password"]

        if "group_id" in update_data and update_data["group_id"] is not None:
            new_group = await self.db_session.get(UserGroup, update_data["group_id"])
            if not new_group:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User group with ID {update_data['group_id']} not found."
                )
            user.group_id = update_data["group_id"]
            del update_data["group_id"]

        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.now(UTC)

        try:
            self.db_session.add(user)
            await self.db_session.commit()
            await self.db_session.refresh(user, attribute_names=["group"])
        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating user: {e}"
            )
        return user

    async def delete_user(self, user_id: int):
        user = await self.db_session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        try:
            await self.db_session.delete(user)
            await self.db_session.commit()
        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting user: {e}"
            )
        return {"message": "User deleted successfully"}
