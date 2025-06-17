from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from src.schemas.movies.genre import GenreOut


class MovieCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    year: Optional[int] = Field(None, gt=1800)
    price: Optional[float] = Field(None, ge=0.0)
    imdb_rating: Optional[float] = Field(None, ge=0.0, le=10.0)
    genre_ids: List[int] = Field(default_factory=list)


class MovieUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    year: Optional[int] = Field(None, gt=1800)
    price: Optional[float] = Field(None, ge=0.0)
    imdb_rating: Optional[float] = Field(None, ge=0.0, le=10.0)
    genre_ids: Optional[List[int]] = None


class MovieOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    year: Optional[int] = None
    price: Optional[float] = None
    imdb_rating: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    genres: List[GenreOut] = Field(default_factory=list)

    class Config:
        from_attributes = True


class PaginatedMovieResponse(BaseModel):
    """Схема для відповіді з пагінованим списком фільмів."""
    total: int
    page: int
    page_size: int
    items: List[MovieOut]