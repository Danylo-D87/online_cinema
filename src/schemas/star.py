from pydantic import BaseModel, Field


class StarCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Повне ім'я зірки/актора")


class StarUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100, description="Нове ім'я зірки/актора")


class StarResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
