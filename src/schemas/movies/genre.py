from pydantic import BaseModel


class GenreBasic(BaseModel):
    name: str


class GenreSchema(GenreBasic):
    """"
               Genre Schema for:

            create / update / delete.
    """
    pass


class GenreResponse(GenreBasic):
    id: int
