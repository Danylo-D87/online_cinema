from pydantic import BaseModel, Field
from typing import Optional


class GenreCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)


class GenreUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)


class GenreOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True