from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.setup import get_db
from src.schemas.user.user import UserRegister, UserLogin, UserResponse, UserActivation, UserRegistrationResponse
from src.schemas.user.token import Token
from src.services.user.auth import AuthService  # Імпортуємо наш новий AuthService
from src.core.dependencies import get_current_user  # Для захисту ендпоінту /users/me
from src.models.user.user import User  # Для типів

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post(
    "/register",
    response_model=UserRegistrationResponse,  # <-- ЗМІНЕНО: Тепер повертаємо цю схему
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Registers a new user and generates an activation token. Account will be inactive until activated."
)
async def register_user_endpoint(
        user_data: UserRegister,
        db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    # Отримуємо об'єкт User та рядок токена
    registered_user_obj, activation_token_value = await auth_service.register_user(user_data)

    # Створюємо об'єкт UserRegistrationResponse для відповіді
    return UserRegistrationResponse(
        user=UserResponse.model_validate(registered_user_obj),  # Валідуємо SQLAlchemy об'єкт через схему
        activation_token=activation_token_value
    )


@router.post(
    "/login",
    response_model=Token,
    summary="User login",
    description="Authenticates a user and returns access and refresh tokens."
)
async def login_for_access_token(
        user_data: UserLogin,
        db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    return await auth_service.login_user(user_data)


@router.post(
    "/refresh_token",
    response_model=Token,
    summary="Refresh access token",
    description="Uses a refresh token to obtain a new access token and potentially a new refresh token."
)
async def refresh_access_token_endpoint(
        refresh_token: str = Depends(
            OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", scheme_name="RefreshTokenScheme")),
        # Використовуємо схему для отримання токена
        db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    return await auth_service.refresh_tokens(refresh_token)


@router.post(
    "/verify-email",
    response_model=UserResponse,
    summary="Verify user email",
    description="Activates a user's account using an activation token."
)
async def verify_email_endpoint(
        activation_data: UserActivation,
        db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    return await auth_service.verify_user_email(activation_data.token)


# Приклад захищеного ендпоінту
@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user information",
    description="Retrieves information about the currently authenticated user.",
    dependencies=[Depends(get_current_user)]  # Захищений ендпоінт
)
async def read_current_user(
        current_user: User = Depends(get_current_user)  # Отримуємо користувача з залежності
):
    return current_user