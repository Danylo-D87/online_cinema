from pydantic import BaseModel, Field


class GenreCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Genre name",
    )


class GenreUpdate(BaseModel):
    name: str | None = Field(
        None,
        min_length=1,
        max_length=50,
        description="New genre name",
    )


class GenreResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
