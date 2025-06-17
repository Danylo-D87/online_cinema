from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.schemas.user.user import UserPublicOut

class RefreshTokenOut(BaseModel):
    id: int
    user_id: int
    token: str
    expires_at: datetime
    created_at: datetime
    user: UserPublicOut

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    """Схема для запиту нового access токена за refresh токеном."""
    refresh_token: str