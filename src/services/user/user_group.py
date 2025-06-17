from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound

from src.models.user.user_group import UserGroup, UserGroupEnum

class UserGroupService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_group_by_name(self, name: UserGroupEnum) -> Optional[UserGroup]:
        """Отримує групу за її іменем."""
        try:
            result = await self.db_session.execute(
                select(UserGroup).filter(UserGroup.name == name.value)
            )
            return result.scalar_one_or_none()
        except NoResultFound:
            return None

    async def get_group_by_id(self, group_id: int) -> Optional[UserGroup]:
        """Отримує групу за її ID."""
        try:
            result = await self.db_session.execute(
                select(UserGroup).filter(UserGroup.id == group_id)
            )
            return result.scalar_one_or_none()
        except NoResultFound:
            return None

    async def get_all_groups(self) -> List[UserGroup]:
        """Отримує всі групи користувачів."""
        result = await self.db_session.execute(
            select(UserGroup)
        )
        return result.scalars().all()

    async def create_initial_groups(self):
        existing_groups = await self.get_all_groups()
        existing_group_names = {g.name for g in existing_groups}

        for group_enum in UserGroupEnum:
            if group_enum.value not in existing_group_names:
                new_group = UserGroup(name=group_enum.value)
                self.db_session.add(new_group)
                print(f"Created initial user group: {group_enum.value}")
        await self.db_session.commit()
        await self.db_session.refresh(new_group)
