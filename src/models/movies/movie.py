from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, UTC

from src.database.base import Base
from src.models.movies.associations import movies_genres


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String)
    year = Column(Integer)
    price = Column(Float)
    imdb_rating = Column(Float)
    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    genres = relationship("Genre", secondary=movies_genres, back_populates="movies")

    def __repr__(self):
        return f"<Movie(name='{self.name}', year={self.year})>"
