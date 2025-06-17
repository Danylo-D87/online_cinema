from sqlalchemy import Table, Column, ForeignKey, Integer
from src.database.base import Base


movies_genres = Table(
    "movies_genres",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id"), primary_key=True),
    Column("genre_id", ForeignKey("genres.id"), primary_key=True),
)
