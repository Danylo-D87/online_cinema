from datetime import datetime
from pydantic import BaseModel

from src.schemas.user.user import UserPublicOut
from src.schemas.movies.movie import MovieOut


class FavoriteMovieCreate(BaseModel):
    movie_id: int


class FavoriteMovieOut(BaseModel):
    id: int
    user_id: int
    movie_id: int
    added_at: datetime
    user: UserPublicOut
    movie: MovieOut

    class Config:
        from_attributes = True
