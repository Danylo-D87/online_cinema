from pydantic import BaseModel, Field


# Схема для створення/оновлення групи користувачів (якщо потрібно)
class UserGroupCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)


class UserGroupUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=50)


# Схема для відповіді групи користувачів
class UserGroupResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
