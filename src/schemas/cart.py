from pydantic import BaseModel
from typing import List, Optional

from src.schemas.cart_item import CartItemResponse
from src.schemas.user import UserResponse

# Схема для створення кошика (в основному, буде створюватися автоматично з User)
class CartCreate(BaseModel):
    user_id: int

# Схема для відповіді, коли відображаємо кошик
class CartResponse(BaseModel):
    id: int
    user_id: int
    items: List[CartItemResponse] = [] # Список елементів кошика
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True
