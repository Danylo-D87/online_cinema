import uuid
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import List, Optional

from src.schemas.genre import GenreResponse
from src.schemas.director import DirectorResponse
from src.schemas.star import StarResponse
from src.schemas.certification import CertificationResponse

# Схема для створення фільму
class MovieCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    year: int = Field(..., ge=1888, description="Рік випуску фільму")
    time: int = Field(..., gt=0, description="Тривалість фільму в хвилинах")
    imdb: float = Field(..., ge=0.0, le=10.0, description="Рейтинг IMDb")
    votes: int = Field(..., ge=0, description="Кількість голосів")
    meta_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="Metascore")
    gross: Optional[float] = Field(None, ge=0.0, description="Валовий дохід (Revenue)")
    description: str = Field(..., min_length=1, max_length=2000)
    price: Decimal = Field(..., decimal_places=2, description="Ціна фільму")

    certification_id: int = Field(..., description="ID сертифікації фільму")
    genre_ids: List[int] = Field([], description="Список ID жанрів для цього фільму")
    director_ids: List[int] = Field([], description="Список ID режисерів для цього фільму")
    star_ids: List[int] = Field([], description="Список ID зірок/акторів для цього фільму")

# Схема для оновлення фільму (всі поля необов'язкові)
class MovieUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    year: Optional[int] = Field(None, ge=1888)
    time: Optional[int] = Field(None, gt=0)
    imdb: Optional[float] = Field(None, ge=0.0, le=10.0)
    votes: Optional[int] = Field(None, ge=0)
    meta_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    gross: Optional[float] = Field(None, ge=0.0)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    price: Optional[Decimal] = Field(None, decimal_places=2)

    certification_id: Optional[int] = None
    genre_ids: Optional[List[int]] = Field(None, description="Оновити список ID жанрів")
    director_ids: Optional[List[int]] = Field(None, description="Оновити список ID режисерів")
    star_ids: Optional[List[int]] = Field(None, description="Оновити список ID зірок/акторів")

# Схема для відповіді (те, що повертаємо клієнту)
class MovieResponse(BaseModel):
    id: int
    uuid: uuid.UUID
    name: str
    year: int
    time: int
    imdb: float
    votes: int
    meta_score: Optional[float] = None
    gross: Optional[float] = None
    description: str
    price: Decimal

    # Вкладені схеми для зв'язків
    certification: CertificationResponse
    genres: List[GenreResponse] = []
    directors: List[DirectorResponse] = []
    stars: List[StarResponse] = []

    class Config:
        from_attributes = True
        # Налаштування для Decimal
        json_encoders = {Decimal: float}
        arbitrary_types_allowed = True
