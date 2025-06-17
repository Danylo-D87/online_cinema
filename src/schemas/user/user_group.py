from pydantic import BaseModel

from src.models.user.user_group import UserGroupEnum


class UserGroupResponse(BaseModel):
    id: int
    name: UserGroupEnum

    class Config:
        from_attributes = True
