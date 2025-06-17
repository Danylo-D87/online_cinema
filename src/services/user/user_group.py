from typing import List
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user.user_group import UserGroup, UserGroupEnum
from src.schemas.user.user_group import UserGroupCreate, UserGroupUpdate, UserGroupEnumSchema


class UserGroupService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_initial_groups(self):
        for group_name_enum in UserGroupEnum:
            group_name = group_name_enum.value
            existing_group = await self.db_session.execute(
                select(UserGroup).where(UserGroup.name == group_name)
            )
            if not existing_group.scalars().first():
                new_group = UserGroup(name=group_name)
                self.db_session.add(new_group)
                await self.db_session.commit()
                await self.db_session.refresh(new_group)
                print(f"Created initial user group: {group_name}")
        await self.db_session.commit()

    async def get_all_user_groups(self) -> List[UserGroup]:
        result = await self.db_session.execute(select(UserGroup))
        return result.scalars().all()

    async def get_user_group_by_id(self, group_id: int) -> UserGroup:
        group = await self.db_session.get(UserGroup, group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User group not found"
            )
        return group

    async def get_user_group_by_name(self, group_name: UserGroupEnumSchema) -> UserGroup:
        group = await self.db_session.execute(
            select(UserGroup).where(UserGroup.name == group_name.value)
        )
        group_obj = group.scalars().first()
        if not group_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User group '{group_name.value}' not found"
            )
        return group_obj

    async def create_user_group(self, group_data: UserGroupCreate) -> UserGroup:
        existing_group = await self.db_session.execute(
            select(UserGroup).where(UserGroup.name == group_data.name.value)
        )
        if existing_group.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User group '{group_data.name.value}' already exists"
            )

        new_group = UserGroup(name=group_data.name.value)
        try:
            self.db_session.add(new_group)
            await self.db_session.commit()
            await self.db_session.refresh(new_group)
        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating user group: {e}"
            )
        return new_group

    async def update_user_group(self, group_id: int, group_data: UserGroupUpdate) -> UserGroup:
        group = await self.db_session.get(UserGroup, group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User group not found"
            )

        if group_data.name:
            existing_group_with_new_name = await self.db_session.execute(
                select(UserGroup).where(UserGroup.name == group_data.name.value, UserGroup.id != group_id)
            )
            if existing_group_with_new_name.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"User group with name '{group_data.name.value}' already exists"
                )
            group.name = group_data.name.value

        try:
            await self.db_session.commit()
            await self.db_session.refresh(group)
        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating user group: {e}"
            )
        return group

    async def delete_user_group(self, group_id: int):
        group = await self.db_session.get(UserGroup, group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User group not found"
            )

        try:
            await self.db_session.delete(group)
            await self.db_session.commit()
        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting user group: {e}"
            )
        return {"message": "User group deleted successfully"}
