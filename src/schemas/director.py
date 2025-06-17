from pydantic import BaseModel, Field


class DirectorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Повне ім'я режисера")


class DirectorUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100, description="Нове ім'я режисера")


class DirectorResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
