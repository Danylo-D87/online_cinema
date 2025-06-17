from datetime import datetime
from pydantic import BaseModel

from src.schemas.user.user import UserPublicOut # Якщо потрібно вкладати User

class ActivationTokenOut(BaseModel):
    id: int
    user_id: int
    token: str
    expires_at: datetime
    created_at: datetime
    user: UserPublicOut # Можна вкласти інформацію про користувача

    class Config:
        from_attributes = True