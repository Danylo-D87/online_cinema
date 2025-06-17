from typing import Optional

from pydantic import BaseModel
from datetime import datetime

from src.schemas.movies.movies import MovieResponse


class FavoriteMovieBase(BaseModel):
    user_id: int
    movie_id: int


class FavoriteMovieCreate(FavoriteMovieBase):
    """Схема для додавання фільму до улюблених."""
    pass


class FavoriteMovieResponse(FavoriteMovieBase):
    """Схема для відповіді API, що відображає улюблені фільми."""
    id: int
    added_at: datetime
    movie: Optional[MovieResponse] = None

    class Config:
        from_attributes = True
