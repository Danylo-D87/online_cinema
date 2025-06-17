from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


# Схема для входу (логіну) користувача
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Схема для повернення токенів після успішного входу
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_at: datetime


# Схема для запиту активації облікового запису (після реєстрації)
class RequestActivation(BaseModel):
    email: EmailStr


# Схема для активації облікового запису
class ActivateAccount(BaseModel):
    token: str


# Схема для запиту скидання пароля
class RequestPasswordReset(BaseModel):
    email: EmailStr


# Схема для самого скидання пароля
class ResetPassword(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


# Схема для відповіді про токен активації/скидання (не повертаємо сам токен, лише статус)
class TokenStatusResponse(BaseModel):
    message: str
    success: bool = True
    token_expires_at: Optional[datetime] = None


# Схема для відкликання refresh токена (вихід)
class TokenRevoke(BaseModel):
    refresh_token: str
