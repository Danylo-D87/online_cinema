from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional

from src.schemas.user_group import UserGroupResponse
from src.schemas.user_profile import UserProfileResponse
from src.schemas.cart import CartResponse


# Схема для реєстрації нового користувача
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


# Схема для створення користувача (можливо, адміном)
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    is_active: Optional[bool] = True
    group_id: Optional[int] = None


# Схема для оновлення даних користувача
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    group_id: Optional[int] = None


# Схема для зміни пароля (коли користувач знає старий пароль)
class UserChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)


# Схема для відповіді користувача (що повертаємо клієнту)
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime
    group: Optional[UserGroupResponse] = None # Вкладена схема групи
    profile: Optional[UserProfileResponse] = None # Вкладена схема профілю
    cart: Optional[CartResponse] = None # Вкладена схема кошика

    class Config:
        from_attributes = True
