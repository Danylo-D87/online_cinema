import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta, UTC
from typing import Optional, List

from src.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token_string,
)

from src.config import settings

from src.models.user.user import User
from src.models.user.refresh_token import RefreshToken
from src.models.user.activation_token import ActivationToken
from src.schemas.user.user import UserCreate, UserLogin, UserUpdate
from src.schemas.user.refresh_token import Token
from src.services.user.user_group import UserGroupService

from fastapi import HTTPException, status


class UserService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.user_group_service = UserGroupService(db_session)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db_session.execute(
            select(User).filter(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        result = await self.db_session.execute(
            select(User).filter(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db_session.execute(
            select(User).filter(User.id == user_id)
        )
        return result.scalar_one_or_none()

    # --- Реєстрація користувача ---
    async def register_user(self, user_data: UserCreate) -> User:
        if await self.get_user_by_email(user_data.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        if await self.get_user_by_username(user_data.username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

        hashed_password = get_password_hash(user_data.password)

        user_group = await self.user_group_service.get_group_by_name("user")
        if not user_group:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Default user group not found.")

        # Створення користувача
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            is_active=False,
            group_id=user_group.id
        )
        self.db_session.add(db_user)
        await self.db_session.flush()

        # Генеруємо токен активації
        activation_token = await self.create_activation_token(db_user.id)

        await self.db_session.commit()
        await self.db_session.refresh(db_user)
        await self.db_session.refresh(activation_token)

        activation_link = f"http://localhost:8000/api/v1/users/activate?token={activation_token.token}"
        print(f"--- АКТИВАЦІЙНИЙ ЛИСТ ДЛЯ {db_user.email} ---")
        print(f"Привіт, {db_user.username}!\n")
        print("Дякуємо за реєстрацію. Будь ласка, перейдіть за посиланням, щоб активувати ваш обліковий запис:")
        print(activation_link)
        print("---------------------------------------")

        return db_user

    # --- Активація користувача ---
    async def activate_user(self, activation_token_string: str) -> User:
        stmt = select(ActivationToken).filter(
            ActivationToken.token == activation_token_string,
            ActivationToken.expires_at > datetime.now(UTC)
        )
        result = await self.db_session.execute(stmt)
        activation_token = result.scalar_one_or_none()

        if not activation_token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired activation token")

        user = await self.get_user_by_id(activation_token.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found for this token")

        if user.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already active")

        user.is_active = True
        await self.db_session.delete(activation_token)
        await self.db_session.commit()
        await self.db_session.refresh(user)
        return user

    # --- Вхід користувача ---
    async def login_user(self, user_data: UserLogin) -> Token:
        user = await self.get_user_by_email(user_data.email)
        if not user or not verify_password(user_data.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account not activated. Please check your email.")

        access_token_data = {"user_id": user.id, "email": user.email, "group_id": user.group_id}
        access_token = create_access_token(access_token_data)

        refresh_token_string = create_refresh_token_string()
        expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        refresh_token_db = RefreshToken(
            user_id=user.id,
            token=refresh_token_string,
            expires_at=expire
        )
        self.db_session.add(refresh_token_db)
        await self.db_session.commit()
        await self.db_session.refresh(refresh_token_db)

        return Token(access_token=access_token, refresh_token=refresh_token_db.token)

    # --- Вихід користувача ---
    async def logout_user(self, refresh_token_string: str) -> None:
        stmt = select(RefreshToken).filter(RefreshToken.token == refresh_token_string)
        result = await self.db_session.execute(stmt)
        refresh_token_db = result.scalar_one_or_none()

        if not refresh_token_db:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token")

        await self.db_session.delete(refresh_token_db)
        await self.db_session.commit()

    # --- Оновлення користувача (адмін або сам користувач) ---
    async def update_user(self, user_id: int, user_data: UserUpdate, current_user_is_admin: bool = False) -> User:
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if user_data.username is not None:
            if await self.get_user_by_username(user_data.username) and user_data.username != user.username:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
            user.username = user_data.username
        if user_data.email is not None:
            if await self.get_user_by_email(user_data.email) and user_data.email != user.email:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
            user.email = user_data.email

        if current_user_is_admin:
            if user_data.is_active is not None:
                user.is_active = user_data.is_active
            if user_data.group_id is not None:
                group = await self.user_group_service.get_group_by_id(user_data.group_id)
                if not group:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid group ID")
                user.group_id = user_data.group_id
        elif (user_data.is_active is not None or user_data.group_id is not None):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can modify user activity status or group.")


        await self.db_session.commit()
        await self.db_session.refresh(user)
        return user

    # --- Отримання списку користувачів (для адмінів) ---
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        result = await self.db_session.execute(
            select(User).offset(skip).limit(limit)
        )
        return result.scalars().all()


    # --- Допоміжні методи для токенів ---
    async def create_activation_token(self, user_id: int) -> ActivationToken:
        token_string = secrets.token_urlsafe(20)
        expires = datetime.now(UTC) + timedelta(hours=24) # Тут можна теж взяти з settings, якщо захочете

        db_token = ActivationToken(
            user_id=user_id,
            token=token_string,
            expires_at=expires
        )
        self.db_session.add(db_token)
        return db_token

    async def get_refresh_token_by_string(self, token: str) -> Optional[RefreshToken]:
        result = await self.db_session.execute(
            select(RefreshToken)
            .filter(RefreshToken.token == token, RefreshToken.expires_at > datetime.now(UTC))
        )
        return result.scalar_one_or_none()

    async def delete_refresh_token(self, refresh_token_db: RefreshToken) -> None:
        await self.db_session.delete(refresh_token_db)
        await self.db_session.commit()

    async def delete_activation_token(self, activation_token_db: ActivationToken) -> None:
        await self.db_session.delete(activation_token_db)
        await self.db_session.commit()