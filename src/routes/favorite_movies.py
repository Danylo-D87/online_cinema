from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.database.setup import get_db
from src.schemas.movies.favorite_movie import FavoriteMovieCreate, FavoriteMovieResponse
from src.services.movies.favorite_movie import FavoriteMovieService
# from src.dependencies.auth import get_current_user

print("Defining favorite_movies router object...")

router = APIRouter(
    prefix="/favorites",
    tags=["Favorite Movies"]
)

@router.post(
    "/",
    response_model=FavoriteMovieResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a movie to favorites",
    description="Adds a specified movie to the current user's favorite list."
)
async def add_movie_to_favorites_endpoint(
    favorite_data: FavoriteMovieCreate, # Приймаємо user_id та movie_id
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user) # Розкоментуйте, якщо потрібна автентифікація
):
    # Якщо використовуєте current_user, замініть favorite_data.user_id на current_user.id
    favorite_service = FavoriteMovieService(db)
    return await favorite_service.add_favorite_movie(
        user_id=favorite_data.user_id, # Або current_user.id
        movie_id=favorite_data.movie_id
    )

@router.delete(
    "/", # Або "/{movie_id}" якщо ви передаєте movie_id в URL, але тіло краще для user_id + movie_id
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a movie from favorites",
    description="Removes a specified movie from the current user's favorite list."
)
async def remove_movie_from_favorites_endpoint(
    favorite_data: FavoriteMovieCreate, # Використовуємо ту ж схему для отримання user_id та movie_id
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    # Якщо використовуєте current_user, замініть favorite_data.user_id на current_user.id
    favorite_service = FavoriteMovieService(db)
    await favorite_service.remove_favorite_movie(
        user_id=favorite_data.user_id, # Або current_user.id
        movie_id=favorite_data.movie_id
    )
    return {} # Для 204 No Content

@router.get(
    "/{user_id}", # Отримуємо улюблені фільми для конкретного user_id
    response_model=List[FavoriteMovieResponse],
    summary="Get all favorite movies for a user",
    description="Retrieves a list of all favorite movies for a given user ID."
)
async def get_user_favorites_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user) # Якщо отримуєте для поточного користувача
):
    # Якщо використовуєте current_user, переконайтеся, що user_id == current_user.id або що у користувача є права
    favorite_service = FavoriteMovieService(db)
    return await favorite_service.get_user_favorite_movies(user_id=user_id) # Або current_user.id

# Якщо потрібен GET за власним ID запису FavoriteMovie
@router.get(
    "/entry/{favorite_id}",
    response_model=FavoriteMovieResponse,
    summary="Get a favorite movie entry by its ID",
    description="Retrieves a single favorite movie entry by its unique ID."
)
async def get_favorite_entry_by_id_endpoint(
    favorite_id: int,
    db: AsyncSession = Depends(get_db)
):
    favorite_service = FavoriteMovieService(db)
    return await favorite_service.get_favorite_movie_by_id(favorite_id)