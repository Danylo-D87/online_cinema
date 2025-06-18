from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

from src.schemas.user.user_group import UserGroupResponse


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr


class UserRegister(UserBase):
    password: str = Field(min_length=6, max_length=100)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    group_id: int
    created_at: datetime
    updated_at: datetime
    group: UserGroupResponse

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)
    is_active: Optional[bool] = None
    group_id: Optional[int] = None


class UserActivation(BaseModel):
    token: str = Field(..., description="Activation token received via email")


class UserUpdateGroup(BaseModel):
    group_id: int = Field(..., description="New group ID for the user")


class UserRegistrationResponse(BaseModel):
    user: UserResponse
    activation_token: Optional[str] = Field(
        None,
        description="The activation token to be sent to the user's email. "
                    "For testing/debugging purposes, it's returned directly. "
                    "In production, it should be sent via email only."
    )
