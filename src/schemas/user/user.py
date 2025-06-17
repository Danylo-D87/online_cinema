# src/schemas/user/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

from src.schemas.user.user_group import UserGroupResponse # Імпортуємо схему групи

# Базова схема користувача
class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr

# Схема для реєстрації нового користувача
class UserRegister(UserBase):
    password: str = Field(min_length=6, max_length=100) # Пароль для реєстрації


# Схема для логіну користувача
class UserLogin(BaseModel):
    username: str
    password: str


# Схема для відповіді з інформацією про користувача
class UserResponse(UserBase):
    id: int
    is_active: bool
    group_id: int
    created_at: datetime
    updated_at: datetime
    group: UserGroupResponse # Додаємо пов'язану групу

    class Config:
        from_attributes = True


# Схема для оновлення користувача (для адміна або самого користувача)
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)
    is_active: Optional[bool] = None # Може бути оновлено адміном
    group_id: Optional[int] = None # Може бути оновлено адміном

# Схема для активації користувача (для ендпоінту верифікації)
class UserActivation(BaseModel):
    token: str = Field(..., description="Activation token received via email")

# Схема для оновлення групи користувача
class UserUpdateGroup(BaseModel):
    group_id: int = Field(..., description="New group ID for the user")


class UserRegistrationResponse(BaseModel):
    """Схема для відповіді після успішної реєстрації, включає активаційний токен."""
    user: UserResponse
    activation_token: Optional[str] = Field(
        None,
        description="The activation token to be sent to the user's email. "
                    "For testing/debugging purposes, it's returned directly. "
                    "In production, it should be sent via email only."
    )
