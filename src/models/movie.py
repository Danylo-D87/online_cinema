import uuid
from datetime import datetime, UTC
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    ForeignKey,
    Table, DECIMAL, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from src.database.base import Base


movie_genres = Table(
    "movie_genres",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True)
)

movie_directors = Table(
    "movie_directors",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id"), primary_key=True),
    Column("director_id", Integer, ForeignKey("directors.id"), primary_key=True)
)

movie_stars = Table(
    "movie_stars",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id"), primary_key=True),
    Column("star_id", Integer, ForeignKey("stars.id"), primary_key=True)
)


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    name = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    time = Column(Integer, nullable=False) # Duration in minutes
    imdb = Column(Float, nullable=False)
    votes = Column(Integer, nullable=False)
    meta_score = Column(Float, nullable=True)
    gross = Column(Float, nullable=True) # Gross revenue
    description = Column(Text, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    certification_id = Column(Integer, ForeignKey("certifications.id"), nullable=False)

    # Constraints
    __table_args__ = (
        UniqueConstraint("name", "year", "time", name="_name_year_time_uc"),
    )

    # Relationships
    certification = relationship("Certification", back_populates="movies")
    genres = relationship("Genre", secondary=movie_genres, backref="movies")
    directors = relationship("Director", secondary=movie_directors, backref="movies")
    stars = relationship("Star", secondary=movie_stars, backref="movies")

    def __repr__(self):
        return f"<Movie(name='{self.name}', year={self.year})>"
