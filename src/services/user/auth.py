from datetime import datetime, timedelta, UTC
import secrets
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.user.user import User
from src.models.user.user_group import UserGroup
from src.models.user.refresh_token import RefreshToken
from src.models.user.activation_token import ActivationToken
from src.schemas.user.user import UserRegister, UserLogin
from src.schemas.user.token import Token
from src.core.security import create_access_token, create_refresh_token, decode_token, PasswordHelper
from src.config.settings import settings


class AuthService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def register_user(self, user_data: UserRegister) -> User: # Важливо, щоб тип повернення був User
        # Перевірка на унікальність username та email
        existing_user = await self.db_session.execute(
            select(User).where(
                (User.username == user_data.username) | (User.email == user_data.email)
            )
        )
        if existing_user.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this username or email already exists"
            )

        # Знайти групу "user" за замовчуванням
        default_group_query = await self.db_session.execute(
            select(UserGroup).where(UserGroup.name == "user")
        )
        default_group = default_group_query.scalars().first()
        if not default_group:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Default 'user' group not found. Please ensure initial groups are created."
            )

        hashed_password = PasswordHelper.get_password_hash(user_data.password)

        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            is_active=False,
            group_id=default_group.id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )

        try:
            self.db_session.add(new_user)
            await self.db_session.commit()

            activation_token_str = secrets.token_urlsafe(32)
            expires_at = datetime.now(UTC) + timedelta(hours=24)

            activation_token_db = ActivationToken(
                user_id=new_user.id,
                token=activation_token_str,
                expires_at=expires_at,
                created_at=datetime.now(UTC)
            )
            self.db_session.add(activation_token_db)
            await self.db_session.commit()
            # await self.db_session.refresh(activation_token_db) # Не потрібно, якщо просто беремо рядок токена

            # Отримуємо користувача з БД з завантаженою групою
            user_from_db_query = await self.db_session.execute(
                select(User).where(User.id == new_user.id).options(selectinload(User.group))
                # <- Повернуто до selectinload
            )
            user_from_db = user_from_db_query.scalars().first()

            if not user_from_db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to retrieve newly registered user after commit."
                )

            # !!! ТУТ ПОВЕРТАЄМО ОБ'ЄКТ, ЯКИЙ FastAPI ЗМОЖЕ СЕРІАЛІЗУВАТИ !!!
            # Тепер ми повертаємо кортеж або об'єкт, який потім буде оброблений в роуті.
            # Змінимо тип повернення функції на кортеж (User, str)
            return user_from_db, activation_token_str  # Повертаємо об'єкт User та рядок токена

        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error during user registration: {type(e).__name__}: {e}"
            )

        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error during user registration: {type(e).__name__}: {e}"
            )

        except Exception as e:
            await self.db_session.rollback()
            # Важливо: якщо ви використовуєте f-string, переконайтеся, що e є коректним для представлення.
            # Краще використовувати logger.error(f"Error during user registration: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error during user registration: {type(e).__name__}: {e}" # Краще для дебагу
            )

    async def verify_user_email(self, activation_token: str) -> User:
        """Активація облікового запису за токеном."""
        token_entry_query = await self.db_session.execute(
            select(ActivationToken)
            .where(ActivationToken.token == activation_token)
            .options(selectinload(ActivationToken.user))
        )
        token_entry = token_entry_query.scalars().first()

        expires_at_aware = token_entry.expires_at
        if expires_at_aware.tzinfo is None:  # Якщо timezone information відсутня (naive datetime)
            expires_at_aware = expires_at_aware.replace(tzinfo=UTC)  # Припускаємо, що це UTC і робимо його aware

        if expires_at_aware < datetime.now(UTC):  # Тепер обидва об'єкти aware
            await self.db_session.delete(token_entry)
            await self.db_session.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Activation token has expired")

        user = token_entry.user
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User associated with token not found")

        if user.is_active:
            await self.db_session.delete(token_entry)  # Видаляємо токен, якщо користувач вже активний
            await self.db_session.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account is already active")

        user.is_active = True
        user.updated_at = datetime.now(UTC)

        try:
            await self.db_session.delete(token_entry)  # Видаляємо використаний токен
            await self.db_session.commit()
            await self.db_session.refresh(user, attribute_names=["group"])  # Оновлюємо користувача і завантажуємо групу
            return user
        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error during account activation: {e}"
            )

    async def login_user(self, user_data: UserLogin) -> Token:
        user_query = await self.db_session.execute(
            select(User)
            .where((User.username == user_data.username) | (User.email == user_data.username))
            .options(selectinload(User.group))  # Завантажуємо групу для ролі
        )
        user = user_query.scalars().first()

        if not user or not PasswordHelper.verify_password(user_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is not active. Please activate your account via email."
            )

        # Створення Access Token
        access_token_payload = {
            "sub": user.username,
            "user_id": user.id,
            "email": user.email,
            "role": user.group.name if user.group else "user"  # Додаємо роль до токена
        }
        access_token = create_access_token(data=access_token_payload)

        # Створення або оновлення Refresh Token
        # Видаляємо старі Refresh Token для цього користувача (опціонально, можна мати кілька)
        await self.db_session.execute(
            select(RefreshToken).where(RefreshToken.user_id == user.id)
        )
        await self.db_session.execute(
            RefreshToken.__table__.delete().where(RefreshToken.user_id == user.id)
        )
        await self.db_session.commit()  # Commit delete operation

        refresh_token_payload = {
            "sub": user.username,
            "user_id": user.id,
            "type": "refresh"  # Маркер для Refresh Token
        }
        refresh_token_str = create_refresh_token(data=refresh_token_payload)

        new_refresh_token_db = RefreshToken(
            user_id=user.id,
            token=refresh_token_str,
            expires_at=datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )

        try:
            self.db_session.add(new_refresh_token_db)
            await self.db_session.commit()
            await self.db_session.refresh(new_refresh_token_db)
        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error saving refresh token: {e}"
            )

        return Token(access_token=access_token, refresh_token=refresh_token_str)

    async def refresh_tokens(self, refresh_token: str) -> Token:
        # Декодуємо Refresh Token, щоб отримати user_id
        payload = decode_token(refresh_token)
        user_id = payload.get("user_id")
        token_type = payload.get("type")

        if not user_id or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Знаходимо Refresh Token у базі даних
        refresh_token_db_query = await self.db_session.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.token == refresh_token)
            .options(selectinload(RefreshToken.user).selectinload(User.group))  # Завантажуємо юзера і його групу
        )
        refresh_token_db = refresh_token_db_query.scalars().first()

        if not refresh_token_db or refresh_token_db.expires_at < datetime.now(UTC):
            # Якщо токен не знайдений або прострочений, видаляємо його (якщо знайшли прострочений)
            if refresh_token_db:
                await self.db_session.delete(refresh_token_db)
                await self.db_session.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = refresh_token_db.user
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Генеруємо новий Access Token
        access_token_payload = {
            "sub": user.username,
            "user_id": user.id,
            "email": user.email,
            "role": user.group.name if user.group else "user"
        }
        new_access_token = create_access_token(data=access_token_payload)

        # Оновлюємо термін дії Refresh Token (або генеруємо новий)
        refresh_token_db.expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token_db.created_at = datetime.now(UTC)  # Оновлюємо дату створення, як оновлений

        try:
            await self.db_session.commit()
            await self.db_session.refresh(refresh_token_db)
        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating refresh token: {e}"
            )

        return Token(access_token=new_access_token, refresh_token=refresh_token_db.token)