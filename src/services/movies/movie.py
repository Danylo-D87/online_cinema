from datetime import datetime, UTC
from typing import List

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.movies import Movie, Genre
from src.schemas.movies.movies import MovieCreate, MovieUpdate
from src.schemas.movies.genre import GenreResponse


class MovieService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_all_movies(self) -> List[Movie]:
        result = await self.db_session.execute(select(Movie).options(selectinload(Movie.genres)))
        return result.scalars().all()

    async def get_movie_by_id(self, movie_id: int) -> Movie:
        movie = await self.db_session.execute(
            select(Movie).options(selectinload(Movie.genres)).where(Movie.id == movie_id)
        )
        movie = movie.scalars().first()

        if not movie:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found"
            )
        return movie

    async def create_movie(self, movie_data: MovieCreate) -> Movie:
        existing_movie = await self.db_session.execute(
            select(Movie).where(Movie.name == movie_data.name)
        )
        if existing_movie.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Movie with this name already exists"
            )

        new_movie = Movie(
            name=movie_data.name,
            description=movie_data.description,
            year=movie_data.year,
            price=movie_data.price,
            imdb_rating=movie_data.imdb_rating,
            created_at=datetime.now(UTC)
        )

        if movie_data.genre_ids:
            genres_to_add = []
            for genre_id in movie_data.genre_ids:
                genre = await self.db_session.get(Genre, genre_id)
                if not genre:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Genre with ID {genre_id} not found."
                    )
                genres_to_add.append(genre)
            new_movie.genres = genres_to_add

        try:
            self.db_session.add(new_movie)
            await self.db_session.commit()
            await self.db_session.refresh(new_movie)
            await self.db_session.execute(
                select(Movie).options(selectinload(Movie.genres)).where(Movie.id == new_movie.id)
            )
            await self.db_session.refresh(new_movie, attribute_names=["genres"])
        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating movie: {e}"
            )
        return new_movie

    async def update_movie(self, movie_id: int, movie_data: MovieUpdate) -> Movie:

        movie_query = await self.db_session.execute(
            select(Movie)
            .options(selectinload(Movie.genres))
            .where(Movie.id == movie_id)
        )
        movie = movie_query.scalars().first()

        if not movie:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found"
            )

        update_fields = movie_data.model_dump(exclude_unset=True, exclude_none=True)

        if "genre_ids" in update_fields:
            genre_ids_to_update = update_fields.pop("genre_ids")

            if genre_ids_to_update is None or len(genre_ids_to_update) == 0:
                movie.genres = []
            else:

                existing_genres_query = await self.db_session.execute(
                    select(Genre).where(Genre.id.in_(genre_ids_to_update))
                )
                existing_genres = existing_genres_query.scalars().all()

                if len(existing_genres) != len(genre_ids_to_update):
                    found_ids = {g.id for g in existing_genres}
                    missing_ids = [gid for gid in genre_ids_to_update if gid not in found_ids]
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Some genres not found: IDs {missing_ids}."
                    )

                movie.genres = existing_genres

        for field, value in update_fields.items():
            setattr(movie, field, value)

        movie.updated_at = datetime.now(UTC)

        try:
            self.db_session.add(movie)
            await self.db_session.commit()
            await self.db_session.refresh(movie)

            await self.db_session.execute(
                select(Movie).options(selectinload(Movie.genres)).where(Movie.id == movie.id)
            )
            await self.db_session.refresh(movie, attribute_names=["genres"])
        except IntegrityError:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A movie with this name already exists."
            )
        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating movie: {e}"
            )
        return movie

    async def delete_movie(self, movie_id: int):
        movie = await self.db_session.get(Movie, movie_id)

        if not movie:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found"
            )

        try:
            await self.db_session.delete(movie)
            await self.db_session.commit()
        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting movie: {e}"
            )
        return {"message": "Movie deleted successfully"}