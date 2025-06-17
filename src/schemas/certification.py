from pydantic import BaseModel, Field


class CertificationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Назва сертифікації (наприклад, PG-13, R)")


class CertificationUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50, description="Нова назва сертифікації")


class CertificationResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
