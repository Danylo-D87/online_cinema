from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator, EmailStr

from src.schemas.user.user_group import UserGroupResponse # Імпортуємо схему для групи



class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None



# --- Схеми для вихідних даних (від сервера до клієнта) ---

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime
    group: UserGroupResponse

    class Config:
        from_attributes = True

class UserPublicOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    group: UserGroupResponse

    class Config:
        from_attributes = True
