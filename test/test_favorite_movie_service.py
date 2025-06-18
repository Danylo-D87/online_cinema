import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, UTC
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.engine import Result

# Import your actual modules
from src.models.movies import FavoriteMovie, Movie
from src.models.user.user import User
from src.models.movies.genre import Genre # Assuming you have a Genre model for Movie.genres

from src.services.movies.favorite_movie import FavoriteMovieService # Ваш сервіс

# --- Helper functions for mocking execute results (reuse from previous tests) ---
def create_mock_execute_result_scalar_first(return_value):
    """
    Creates a mock object that simulates the result of db_session.execute().scalars().first()
    for reliable mocking of SQLAlchemy queries.
    """
    mock_scalars_call = MagicMock()
    mock_scalars_call.first.return_value = return_value # Directly return value for first()

    mock_execute_return = AsyncMock(spec=Result)
    mock_execute_return.scalars.return_value = mock_scalars_call
    return mock_execute_return

def create_mock_execute_result_scalar_all(return_value_list):
    """
    Creates a mock object that simulates the result of db_session.execute().scalars().all()
    """
    mock_scalars_call = MagicMock()
    mock_scalars_call.all.return_value = return_value_list

    mock_execute_return = AsyncMock(spec=Result)
    mock_execute_return.scalars.return_value = mock_scalars_call
    return mock_execute_return

def create_mock_execute_result_dml():
    """
    Creates a mock object that simulates the result of db_session.execute() for DML operations.
    """
    mock_result = AsyncMock(spec=Result)
    mock_result.rowcount = 1  # Example for delete or update
    return mock_result


# --- Fixtures and Mocks for Tests ---

@pytest.fixture
def mock_db_session():
    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value = create_mock_execute_result_scalar_first(None) # Default
    session.commit.return_value = None
    session.rollback.return_value = None
    session.add.return_value = None
    session.delete.return_value = None
    session.refresh.return_value = None # Default refresh behavior
    session.get.return_value = None # Default get behavior
    yield session

@pytest.fixture
def favorite_movie_service(mock_db_session):
    service = FavoriteMovieService(mock_db_session)
    yield service

@pytest.fixture
def mock_user():
    user = MagicMock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.email = "testuser@example.com"
    return user

@pytest.fixture
def mock_movie():
    movie = MagicMock(spec=Movie)
    movie.id = 101
    movie.title = "Test Movie"
    movie.description = "A great movie for testing."
    movie.release_date = datetime(2023, 1, 1, tzinfo=UTC)
    movie.rating = 8.5
    movie.poster_url = "http://example.com/poster.jpg"
    movie.trailer_url = "http://example.com/trailer.mp4"
    movie.genres = [] # Add if needed for specific tests
    return movie

@pytest.fixture
def mock_genre():
    genre = MagicMock(spec=Genre)
    genre.id = 1
    genre.name = "Action"
    return genre

@pytest.fixture
def mock_favorite_movie(mock_user, mock_movie):
    favorite = MagicMock(spec=FavoriteMovie)
    favorite.id = 1
    favorite.user_id = mock_user.id
    favorite.movie_id = mock_movie.id
    favorite.added_at = datetime.now(UTC)
    favorite.user = mock_user
    favorite.movie = mock_movie
    return favorite

# --- Tests for FavoriteMovieService.add_favorite_movie ---

@pytest.mark.asyncio
async def test_add_favorite_movie_user_not_found(favorite_movie_service, mock_db_session, mock_movie):
    mock_db_session.get.side_effect = [None, mock_movie] # User not found

    with pytest.raises(HTTPException) as exc_info:
        await favorite_movie_service.add_favorite_movie(999, mock_movie.id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "User not found"
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()

@pytest.mark.asyncio
async def test_add_favorite_movie_movie_not_found(favorite_movie_service, mock_db_session, mock_user):
    mock_db_session.get.side_effect = [mock_user, None] # Movie not found

    with pytest.raises(HTTPException) as exc_info:
        await favorite_movie_service.add_favorite_movie(mock_user.id, 999)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Movie not found"
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()

@pytest.mark.asyncio
async def test_add_favorite_movie_already_in_favorites(favorite_movie_service, mock_db_session, mock_user, mock_movie, mock_favorite_movie):
    mock_db_session.get.side_effect = [mock_user, mock_movie]
    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_first(mock_favorite_movie) # Existing favorite found
    ]

    with pytest.raises(HTTPException) as exc_info:
        await favorite_movie_service.add_favorite_movie(mock_user.id, mock_movie.id)

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert exc_info.value.detail == "Movie already in favorites for this user"
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()

@pytest.mark.asyncio
async def test_add_favorite_movie_db_error(favorite_movie_service, mock_db_session, mock_user, mock_movie):
    mock_db_session.get.side_effect = [mock_user, mock_movie]
    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_first(None) # No existing favorite
    ]
    mock_db_session.add.side_effect = Exception("Simulated DB error on add")

    with pytest.raises(HTTPException) as exc_info:
        await favorite_movie_service.add_favorite_movie(mock_user.id, mock_movie.id)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error adding movie to favorites" in exc_info.value.detail
    mock_db_session.rollback.assert_called_once()
    mock_db_session.commit.assert_not_called()


# --- Tests for FavoriteMovieService.remove_favorite_movie ---

@pytest.mark.asyncio
async def test_remove_favorite_movie_success(favorite_movie_service, mock_db_session, mock_favorite_movie):
    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_first(mock_favorite_movie) # Favorite entry found
    ]

    response = await favorite_movie_service.remove_favorite_movie(
        mock_favorite_movie.user_id, mock_favorite_movie.movie_id
    )

    mock_db_session.execute.assert_called_once()
    mock_db_session.delete.assert_called_once_with(mock_favorite_movie)
    mock_db_session.commit.assert_called_once()
    assert response == {"message": "Movie removed from favorites successfully"}

@pytest.mark.asyncio
async def test_remove_favorite_movie_not_found(favorite_movie_service, mock_db_session):
    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_first(None) # Favorite entry not found
    ]

    with pytest.raises(HTTPException) as exc_info:
        await favorite_movie_service.remove_favorite_movie(1, 101)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Movie not found in favorites for this user"
    mock_db_session.delete.assert_not_called()
    mock_db_session.commit.assert_not_called()

@pytest.mark.asyncio
async def test_remove_favorite_movie_db_error(favorite_movie_service, mock_db_session, mock_favorite_movie):
    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_first(mock_favorite_movie) # Favorite entry found
    ]
    mock_db_session.delete.side_effect = Exception("Simulated DB error on delete")

    with pytest.raises(HTTPException) as exc_info:
        await favorite_movie_service.remove_favorite_movie(
            mock_favorite_movie.user_id, mock_favorite_movie.movie_id
        )

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error removing movie from favorites" in exc_info.value.detail
    mock_db_session.rollback.assert_called_once()
    mock_db_session.commit.assert_not_called()

# --- Tests for FavoriteMovieService.get_user_favorite_movies ---

@pytest.mark.asyncio
async def test_get_user_favorite_movies_success(favorite_movie_service, mock_db_session, mock_user, mock_favorite_movie, mock_movie, mock_genre):
    # Ensure movie has genres for selectinload
    mock_movie.genres = [mock_genre]
    mock_favorite_movie.movie = mock_movie # Ensure the favorite object linked movie has genres
    mock_favorite_movie.user = mock_user

    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_all([mock_favorite_movie]) # Return a list of favorite movies
    ]

    favorites = await favorite_movie_service.get_user_favorite_movies(mock_user.id)

    mock_db_session.execute.assert_called_once()
    assert len(favorites) == 1
    assert favorites[0] == mock_favorite_movie
    assert favorites[0].user == mock_user
    assert favorites[0].movie == mock_movie
    assert favorites[0].movie.genres[0] == mock_genre


@pytest.mark.asyncio
async def test_get_user_favorite_movies_no_favorites(favorite_movie_service, mock_db_session, mock_user):
    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_all([]) # Return empty list
    ]

    favorites = await favorite_movie_service.get_user_favorite_movies(mock_user.id)

    mock_db_session.execute.assert_called_once()
    assert len(favorites) == 0
    assert favorites == []

# --- Tests for FavoriteMovieService.get_favorite_movie_by_id ---

@pytest.mark.asyncio
async def test_get_favorite_movie_by_id_success(favorite_movie_service, mock_db_session, mock_favorite_movie, mock_user, mock_movie, mock_genre):
    # Ensure nested relationships are mocked for selectinload
    mock_movie.genres = [mock_genre]
    mock_favorite_movie.user = mock_user
    mock_favorite_movie.movie = mock_movie

    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_first(mock_favorite_movie) # Favorite entry found
    ]

    favorite = await favorite_movie_service.get_favorite_movie_by_id(mock_favorite_movie.id)

    mock_db_session.execute.assert_called_once()
    assert favorite == mock_favorite_movie
    assert favorite.user == mock_user
    assert favorite.movie == mock_movie
    assert favorite.movie.genres[0] == mock_genre


@pytest.mark.asyncio
async def test_get_favorite_movie_by_id_not_found(favorite_movie_service, mock_db_session):
    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_first(None) # Favorite entry not found
    ]

    with pytest.raises(HTTPException) as exc_info:
        await favorite_movie_service.get_favorite_movie_by_id(999)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Favorite movie entry not found"
    mock_db_session.execute.assert_called_once()