from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.setup import get_db
from src.schemas.movies.genre import GenreSchema, GenreResponse
from src.services.movies import genre as genre_services


router = APIRouter(prefix="/genres", tags=["Genres"])


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=list[GenreResponse],
    summary="Get all genres",
    description="Get all genres from the database",
    response_description="List of genres",
)
async def get_all_genres_endpoint(db: AsyncSession = Depends(get_db)):
    genres = await genre_services.get_all_genres(db)
    return genres


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=GenreResponse,
    summary="Create a new genre",
    description="Create a new genre in the database",
    response_description="New genre",
)
async def create_genre_endpoint(
        genre_data: GenreSchema,
        db: AsyncSession = Depends(get_db),
):
    genre = await genre_services.create_genre(db, genre_data)
    return genre


@router.put(
    "/{genre_id}",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=GenreResponse,
    summary="Update a genre",
    description="Update a genre in the database",
    response_description="Updated genre",
)
async def update_genre_endpoint(
        genre_id: int,
        genre_data: GenreSchema,
        db: AsyncSession = Depends(get_db),
):
    genre = await genre_services.update_genre(db, genre_id, genre_data)
    return genre


@router.delete("/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_genre_endpoint(
    genre_id: int,
    db: AsyncSession = Depends(get_db)
):
    await genre_services.delete_genre(db, genre_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)