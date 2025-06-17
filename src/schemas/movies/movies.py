from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

from src.schemas.movies.genre import GenreResponse


class MovieBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    year: int = Field(gt=1800)
    price: float = Field(ge=0.0)
    imdb_rating: float = Field(ge=0.0, le=10.0)


class MovieCreate(MovieBase):
    genre_ids: Optional[List[int]] = Field(None, description="List of Genre IDs for the movie")


class MovieUpdate(MovieBase):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    year: Optional[int] = Field(None, gt=1800)
    price: Optional[float] = Field(None, ge=0.0)
    imdb_rating: Optional[float] = Field(None, ge=0.0, le=10.0)
    genre_ids: Optional[List[int]] = Field(None, description="List of Genre IDs to update for the movie")


class MovieResponse(MovieBase):
    id: int
    created_at: datetime
    updated_at: datetime
    genres: List[GenreResponse] = []

    class Config:
        from_attributes = True
