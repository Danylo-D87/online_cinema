from datetime import datetime, UTC
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    ForeignKey,
    Table,
)
from sqlalchemy.orm import relationship
from src.database.base import Base


movie_genre_association = Table(
    'movie_genre_association',
    Base.metadata,
    Column('movie_id', Integer, ForeignKey('movies.id'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('genres.id'), primary_key=True)
)


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    release_date = Column(DateTime, nullable=True)
    poster_url = Column(String, nullable=True)
    trailer_url = Column(String, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    rating = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(
        DateTime,
        default=datetime.now(UTC),
        onupdate=datetime.now(UTC),
    )

    genres = relationship(
        "Genre",
        secondary=movie_genre_association,
        backref="movies"
    )

    def __repr__(self):
        return (
            f"<Movie(title='{self.title}', release_date='"
            f"{self.release_date.year if self.release_date else 'N/A'}')>")
