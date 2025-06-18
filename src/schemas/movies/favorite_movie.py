from typing import Optional

from pydantic import BaseModel
from datetime import datetime

from src.schemas.movies.movies import MovieResponse


class FavoriteMovieBase(BaseModel):
    user_id: int
    movie_id: int


class FavoriteMovieCreate(FavoriteMovieBase):
    pass


class FavoriteMovieResponse(FavoriteMovieBase):
    id: int
    added_at: datetime
    movie: Optional[MovieResponse] = None

    class Config:
        from_attributes = True
