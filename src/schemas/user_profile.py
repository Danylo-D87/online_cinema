from pydantic import BaseModel, Field, HttpUrl
from datetime import date
from typing import Optional
from src.models.user_profile import GenderEnum


# Схема для створення профілю користувача
class UserProfileCreate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    avatar: Optional[HttpUrl] = None
    gender: Optional[GenderEnum] = None
    date_of_birth: Optional[date] = None
    info: Optional[str] = Field(None, max_length=1000)


# Схема для оновлення профілю користувача
class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    avatar: Optional[HttpUrl] = None
    gender: Optional[GenderEnum] = None
    date_of_birth: Optional[date] = None
    info: Optional[str] = Field(None, max_length=1000)


# Схема для відповіді профілю користувача
class UserProfileResponse(BaseModel):
    id: int
    user_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar: Optional[HttpUrl] = None
    gender: Optional[GenderEnum] = None
    date_of_birth: Optional[date] = None
    info: Optional[str] = None

    class Config:
        from_attributes = True
