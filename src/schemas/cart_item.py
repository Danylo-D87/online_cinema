from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from src.schemas.movie import MovieResponse


class CartItemCreate(BaseModel):
    movie_id: int


# Схема для відповіді, коли відображаємо елемент кошика
class CartItemResponse(BaseModel):
    id: int
    cart_id: int
    movie_id: int
    added_at: datetime
    movie: Optional[MovieResponse] = None

    class Config:
        from_attributes = True
