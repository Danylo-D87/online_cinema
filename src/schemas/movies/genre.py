from pydantic import BaseModel


class GenreBase(BaseModel):
    name: str


class GenreSchema(GenreBase):
    pass


class GenreResponse(GenreBase):
    id: int
