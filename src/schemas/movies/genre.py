from pydantic import BaseModel


class GenreBase(BaseModel):
    name: str


class GenreSchema(GenreBase):
    """"
               Genre Schema for:

            create / update / delete.
    """
    pass


class GenreResponse(GenreBase):
    id: int
