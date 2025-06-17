from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from src.database.base import Base


class FavoriteMovie(Base):
    __tablename__ = "favorite_movies"
    __table_args__ = (UniqueConstraint('user_id', 'movie_id', name='_user_movie_uc'),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    added_at = Column(DateTime, default=datetime.now(UTC))

    user = relationship("User", back_populates="favorite_movies")
    movie = relationship("Movie", back_populates="favorite_movies")
