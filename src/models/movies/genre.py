from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.database.base import Base
from src.models.movies.associations import movies_genres


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)

    movies = relationship("Movie", secondary=movies_genres, back_populates="genres")

    def __repr__(self):
        return f"<Genre(name='{self.name}')>"
