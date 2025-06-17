from datetime import datetime

from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    # expires_in: int # Термін дії Access Token у секундах, можна додати

class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None # Додаємо поле ролі для JWT

class ActivationTokenResponse(BaseModel):
    token: str
    expires_at: datetime

class RefreshTokenResponse(BaseModel):
    token: str
    expires_at: datetime