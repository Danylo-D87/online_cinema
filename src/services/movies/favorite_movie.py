from datetime import datetime, UTC
from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.movies import FavoriteMovie, Movie
from src.models.user.user import User


class FavoriteMovieService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def add_favorite_movie(self, user_id: int, movie_id: int) -> FavoriteMovie:
        user = await self.db_session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        movie = await self.db_session.get(Movie, movie_id)
        if not movie:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

        existing_favorite = await self.db_session.execute(
            select(FavoriteMovie)
            .where(FavoriteMovie.user_id == user_id, FavoriteMovie.movie_id == movie_id)
        )
        if existing_favorite.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Movie already in favorites for this user"
            )

        new_favorite = FavoriteMovie(
            user_id=user_id,
            movie_id=movie_id,
            added_at=datetime.now(UTC)
        )

        try:
            self.db_session.add(new_favorite)
            await self.db_session.commit()
            await self.db_session.refresh(new_favorite)
            await self.db_session.execute(
                select(FavoriteMovie)
                .options(selectinload(FavoriteMovie.user), selectinload(FavoriteMovie.movie))
                .where(FavoriteMovie.id == new_favorite.id)
            )
            await self.db_session.refresh(new_favorite, attribute_names=["user", "movie"])
        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error adding movie to favorites: {e}"
            )
        return new_favorite

    async def remove_favorite_movie(self, user_id: int, movie_id: int):
        favorite_entry = await self.db_session.execute(
            select(FavoriteMovie)
            .where(FavoriteMovie.user_id == user_id, FavoriteMovie.movie_id == movie_id)
        )
        favorite_entry = favorite_entry.scalars().first()

        if not favorite_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found in favorites for this user"
            )

        try:
            await self.db_session.delete(favorite_entry)
            await self.db_session.commit()
        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error removing movie from favorites: {e}"
            )
        return {"message": "Movie removed from favorites successfully"}

    async def get_user_favorite_movies(self, user_id: int) -> List[FavoriteMovie]:
        result = await self.db_session.execute(
            select(FavoriteMovie)
            .options(selectinload(FavoriteMovie.movie).selectinload(Movie.genres), selectinload(FavoriteMovie.user))
            .where(FavoriteMovie.user_id == user_id)
        )
        return result.scalars().all()

    async def get_favorite_movie_by_id(self, favorite_id: int) -> FavoriteMovie:
        favorite_entry = await self.db_session.execute(
            select(FavoriteMovie)
            .options(selectinload(FavoriteMovie.user), selectinload(FavoriteMovie.movie).selectinload(Movie.genres))
            .where(FavoriteMovie.id == favorite_id)
        )
        favorite_entry = favorite_entry.scalars().first()
        if not favorite_entry:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite movie entry not found")
        return favorite_entry
