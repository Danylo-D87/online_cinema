from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum as PyEnum


class UserGroupEnumSchema(PyEnum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class UserGroupBase(BaseModel):
    name: UserGroupEnumSchema = Field(description="Name of the user group (e.g., 'user', 'moderator', 'admin')")


class UserGroupCreate(UserGroupBase):
    pass


class UserGroupUpdate(BaseModel):
    name: Optional[UserGroupEnumSchema] = Field(None, description="New name for the user group")


class UserGroupResponse(UserGroupBase):
    id: int

    class Config:
        from_attributes = True
