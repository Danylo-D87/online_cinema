from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.movies.genre import Genre
from src.schemas.movies.genre import GenreSchema


async def get_all_genres(db: AsyncSession):
    result = await db.execute(select(Genre))
    return result.scalars().all()


async def create_genre(db: AsyncSession, genre_name: GenreSchema):

    existing_genre = await db.execute(select(Genre).where(Genre.name == genre_name.name))

    if existing_genre.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST ,
            detail="Genre already exists",
        )

    new_genre = Genre(name=genre_name.name)

    try:
        db.add(new_genre)
        await db.commit()
        await db.refresh(new_genre)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating genre: {e}"
        )

    return new_genre


async def update_genre(
        db: AsyncSession,
        genre_id: int,
        genre_name: GenreSchema,
):
    genre = await db.get(Genre, genre_id)

    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found"
        )

    genre.name = genre_name.name

    try:
        db.add(genre)
        await db.commit()
        await db.refresh(genre)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating genre: {e}"
        )

    return genre


async def delete_genre(db: AsyncSession, genre_id: int):
    genre = await db.get(Genre, genre_id)

    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found"
        )

    try:
        await db.delete(genre)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting genre: {e}"
        )
