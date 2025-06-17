from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.database.setup import get_db
from src.schemas.movies.movies import MovieCreate, MovieUpdate, MovieResponse
from src.services.movies.movie import MovieService

router = APIRouter(
    prefix="/movies",
    tags=["Movies"]
)

@router.post(
    "/",
    response_model=MovieResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new movie",
    description="Creates a new movie with the provided details and associates it with genres."
)
async def create_movie_endpoint(
    movie_data: MovieCreate,
    db: AsyncSession = Depends(get_db)
):
    movie_service = MovieService(db)
    return await movie_service.create_movie(movie_data)


@router.get(
    "/",
    response_model=List[MovieResponse],
    summary="Get all movies",
    description="Retrieves a list of all movies with their associated genres."
)
async def get_all_movies_endpoint(db: AsyncSession = Depends(get_db)):
    movie_service = MovieService(db)
    return await movie_service.get_all_movies()


@router.get(
    "/{movie_id}",
    response_model=MovieResponse,
    summary="Get movie by ID",
    description="Retrieves a single movie by its ID, including associated genres."
)
async def get_movie_by_id_endpoint(
    movie_id: int,
    db: AsyncSession = Depends(get_db)
):
    movie_service = MovieService(db)
    return await movie_service.get_movie_by_id(movie_id)


@router.put(
    "/{movie_id}",
    response_model=MovieResponse,
    summary="Update a movie",
    description="Updates an existing movie by its ID, including its associated genres."
)
async def update_movie_endpoint(
    movie_id: int,
    movie_data: MovieUpdate,
    db: AsyncSession = Depends(get_db)
):
    movie_service = MovieService(db)
    return await movie_service.update_movie(movie_id, movie_data)


@router.delete(
    "/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a movie",
    description="Deletes a movie by its ID."
)
async def delete_movie_endpoint(
    movie_id: int,
    db: AsyncSession = Depends(get_db)
):
    movie_service = MovieService(db)
    await movie_service.delete_movie(movie_id)
    return {} # Return empty response for 204 No Content