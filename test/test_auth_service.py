import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta, UTC
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.engine import Result
from passlib.context import CryptContext

# Import your actual modules
from src.models.user.user import User
from src.models.user.user_group import UserGroup
from src.models.user.refresh_token import RefreshToken
from src.models.user.activation_token import ActivationToken

from src.schemas.user.user import UserRegister, UserLogin
from src.schemas.user.token import Token

# --- Passlib for mocks ---
pwd_context_for_testing = CryptContext(schemes=["bcrypt"], deprecated="auto")
MOCKED_PASSWORD_HASH = pwd_context_for_testing.hash("test_password_for_mocking")


# --- Helper function for mocking execute results ---
def create_mock_execute_result_scalar_first(return_value):
    """
    Creates a mock object that simulates the result of db_session.execute().scalars().first()
    for reliable mocking of SQLAlchemy queries.
    """
    mock_first_call = MagicMock(return_value=return_value)
    mock_scalars_call = MagicMock()
    mock_scalars_call.first.return_value = mock_first_call()

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
    session.execute.return_value = create_mock_execute_result_scalar_first(None)  # Default
    session.commit.return_value = None
    session.rollback.return_value = None
    session.add.return_value = None
    session.delete.return_value = None
    session.refresh.return_value = None
    yield session


@pytest.fixture
def auth_service(mock_db_session):
    # Patch all external dependencies within this fixture
    with patch('src.core.security.PasswordHelper', autospec=True) as mock_ph, \
            patch('src.services.user.auth.create_access_token') as mock_create_access_token, \
            patch('src.services.user.auth.create_refresh_token') as mock_create_refresh_token, \
            patch('src.services.user.auth.decode_token') as mock_decode_token, \
            patch('src.services.user.auth.settings') as mock_settings, \
            patch('secrets.token_urlsafe', return_value="mock_activation_token_string") as mock_token_urlsafe:
        # Set default return values for mocks
        mock_ph.get_password_hash.return_value = MOCKED_PASSWORD_HASH
        mock_ph.verify_password.return_value = True  # Default true, can be overridden in tests
        mock_create_access_token.return_value = "mock_access_token_value"
        mock_create_refresh_token.return_value = "mock_refresh_token_value"
        mock_decode_token.return_value = {"user_id": 1, "type": "refresh", "sub": "testuser"}

        # Mock settings attributes
        mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 15
        mock_settings.REFRESH_TOKEN_EXPIRE_DAYS = 7
        mock_settings.SECRET_KEY = "test_secret_key"
        mock_settings.ALGORITHM = "HS256"

        # Import AuthService HERE, after all patches are applied
        from src.services.user.auth import AuthService as RealAuthService
        service = RealAuthService(mock_db_session)

        # Attach mocks to the service object for easy access in tests
        service.mock_ph = mock_ph
        service.mock_create_access_token = mock_create_access_token
        service.mock_create_refresh_token = mock_create_refresh_token
        service.mock_decode_token = mock_decode_token
        service.mock_settings = mock_settings
        service.mock_token_urlsafe = mock_token_urlsafe

        yield service


# --- Test Data (Mock Models) ---

@pytest.fixture
def user_register_data():
    return UserRegister(username="newuser", email="newuser@example.com", password="password123")


@pytest.fixture
def user_login_data():
    return UserLogin(username="testuser", password="password123")


@pytest.fixture
def mock_user_group():
    group = MagicMock(spec=UserGroup)
    group.id = 1
    group.name = "user"
    return group


@pytest.fixture
def mock_active_user(mock_user_group):
    user = MagicMock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.email = "testuser@example.com"
    user.password_hash = MOCKED_PASSWORD_HASH
    user.is_active = True
    user.group = mock_user_group
    user.group_id = mock_user_group.id
    user.created_at = datetime.now(UTC) - timedelta(days=1)
    user.updated_at = datetime.now(UTC) - timedelta(days=1)
    user.favorite_movies = []
    user.refresh_tokens = []
    user.activation_tokens = []
    return user


@pytest.fixture
def mock_inactive_user(mock_user_group):
    user = MagicMock(spec=User)
    user.id = 2
    user.username = "inactiveuser"
    user.email = "inactiveuser@example.com"
    user.password_hash = MOCKED_PASSWORD_HASH
    user.is_active = False
    user.group = mock_user_group
    user.group_id = mock_user_group.id
    user.created_at = datetime.now(UTC) - timedelta(days=1)
    user.updated_at = datetime.now(UTC) - timedelta(days=1)
    user.favorite_movies = []
    user.refresh_tokens = []
    user.activation_tokens = []
    return user


@pytest.fixture
def mock_activation_token(mock_inactive_user):
    token = MagicMock(spec=ActivationToken)
    token.user_id = mock_inactive_user.id
    token.token = "valid_activation_token_123"
    token.expires_at = datetime.now(UTC) + timedelta(hours=1)
    token.created_at = datetime.now(UTC)
    token.user = mock_inactive_user
    return token


@pytest.fixture
def mock_expired_activation_token(mock_inactive_user):
    token = MagicMock(spec=ActivationToken)
    token.user_id = mock_inactive_user.id
    token.token = "expired_activation_token_abc"
    token.expires_at = datetime.now(UTC) - timedelta(hours=1)
    token.created_at = datetime.now(UTC) - timedelta(days=2)
    token.user = mock_inactive_user
    return token


@pytest.fixture
def mock_refresh_token_db_obj(mock_active_user):
    refresh_token = MagicMock(spec=RefreshToken)
    refresh_token.user_id = mock_active_user.id
    refresh_token.token = "valid_refresh_token_xyz"
    refresh_token.expires_at = datetime.now(UTC) + timedelta(days=7)
    refresh_token.created_at = datetime.now(UTC)
    refresh_token.user = mock_active_user
    return refresh_token


@pytest.fixture
def mock_expired_refresh_token_db_obj(mock_active_user):
    refresh_token = MagicMock(spec=RefreshToken)
    refresh_token.user_id = mock_active_user.id
    refresh_token.token = "expired_refresh_token_123"
    refresh_token.expires_at = datetime.now(UTC) - timedelta(days=1)
    refresh_token.created_at = datetime.now(UTC) - timedelta(days=8)
    refresh_token.user = mock_active_user
    return refresh_token


# --- Tests for AuthService.register_user ---

@pytest.mark.asyncio
async def test_register_user_success(auth_service, mock_db_session, user_register_data, mock_user_group):
    mock_new_user_instance_after_commit = MagicMock(
        spec=User,
        id=1,
        username=user_register_data.username,
        email=user_register_data.email,
        password_hash=MOCKED_PASSWORD_HASH,
        is_active=False,
        group=mock_user_group,
        group_id=mock_user_group.id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_first(None),  # 1. Check for existing user (None)
        create_mock_execute_result_scalar_first(mock_user_group),  # 2. Find default group
        create_mock_execute_result_scalar_first(mock_new_user_instance_after_commit)
        # 3. Retrieve newly created user after initial commit
    ]

    user, activation_token_str = await auth_service.register_user(user_register_data)

    auth_service.mock_ph.get_password_hash.assert_called_once_with(user_register_data.password)
    auth_service.mock_token_urlsafe.assert_called_once()

    assert mock_db_session.add.call_count == 2
    assert isinstance(mock_db_session.add.call_args_list[0].args[0], User)
    assert isinstance(mock_db_session.add.call_args_list[1].args[0], ActivationToken)

    assert mock_db_session.commit.call_count == 2
    mock_db_session.rollback.assert_not_called()

    assert user.username == user_register_data.username
    assert user.email == user_register_data.email
    assert user.is_active is False
    assert user.group.name == "user"
    assert activation_token_str == "mock_activation_token_string"


@pytest.mark.asyncio
async def test_register_user_existing_user(auth_service, mock_db_session, user_register_data, mock_active_user):
    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_first(mock_active_user)  # User already exists
    ]

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.register_user(user_register_data)

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert "User with this username or email already exists" in exc_info.value.detail
    mock_db_session.commit.assert_not_called()
    mock_db_session.rollback.assert_not_called()


@pytest.mark.asyncio
async def test_register_user_no_default_group(auth_service, mock_db_session, user_register_data):
    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_first(None),  # No existing user
        create_mock_execute_result_scalar_first(None)  # No default group found
    ]

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.register_user(user_register_data)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Default 'user' group not found. Please ensure initial groups are created." in exc_info.value.detail
    mock_db_session.commit.assert_not_called()
    mock_db_session.rollback.assert_not_called()


@pytest.mark.asyncio
async def test_register_user_db_commit_error(auth_service, mock_db_session, user_register_data, mock_user_group):
    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_first(None),  # No existing user
        create_mock_execute_result_scalar_first(mock_user_group)  # Default group found
    ]
    mock_db_session.commit.side_effect = [
        Exception("Database error during user commit"),  # First commit (for user) fails
        None
    ]

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.register_user(user_register_data)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error during user registration" in exc_info.value.detail
    mock_db_session.rollback.assert_called_once()
    mock_db_session.add.assert_called_once()


# --- Tests for AuthService.verify_user_email ---

@pytest.mark.asyncio
async def test_verify_user_email_success(auth_service, mock_db_session, mock_activation_token, mock_inactive_user,
                                         mock_user_group):
    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_first(mock_activation_token)
    ]
    mock_db_session.refresh.side_effect = lambda obj, attribute_names=None: setattr(obj, 'group',
                                                                                    mock_user_group) if isinstance(obj,
                                                                                                                   MagicMock) and "group" in (
                                                                                                                    attribute_names or []) else None

    user = await auth_service.verify_user_email(mock_activation_token.token)

    mock_db_session.execute.assert_called_once()
    assert user.is_active is True
    mock_db_session.delete.assert_called_once_with(mock_activation_token)
    assert mock_db_session.commit.call_count == 1
    mock_db_session.refresh.assert_called_once_with(user, attribute_names=["group"])
    assert user.username == mock_inactive_user.username
    assert user.group.name == mock_user_group.name


@pytest.mark.asyncio
async def test_verify_user_email_invalid_token(auth_service, mock_db_session):
    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_first(None)  # Token not found in DB
    ]

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.verify_user_email("non_existent_token")

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Activation token not found"

    mock_db_session.delete.assert_not_called()
    mock_db_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_verify_user_email_expired_token(auth_service, mock_db_session, mock_expired_activation_token):
    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_first(mock_expired_activation_token)
    ]

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.verify_user_email(mock_expired_activation_token.token)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Activation token has expired" in exc_info.value.detail
    mock_db_session.delete.assert_called_once_with(mock_expired_activation_token)
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_verify_user_email_already_active(auth_service, mock_db_session, mock_activation_token, mock_active_user):
    mock_activation_token.user = mock_active_user

    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_first(mock_activation_token)
    ]

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.verify_user_email(mock_activation_token.token)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Account is already active" in exc_info.value.detail
    mock_db_session.delete.assert_called_once_with(mock_activation_token)
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_verify_user_email_user_not_found_for_token(auth_service, mock_db_session, mock_activation_token):
    mock_activation_token.user = None

    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_first(mock_activation_token)
    ]

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.verify_user_email(mock_activation_token.token)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "User associated with token not found" in exc_info.value.detail
    mock_db_session.delete.assert_not_called()
    mock_db_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_verify_user_email_db_error(auth_service, mock_db_session, mock_activation_token, mock_inactive_user):
    mock_activation_token.user = mock_inactive_user

    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_first(mock_activation_token)
    ]
    mock_db_session.commit.side_effect = Exception("DB connection lost during activation")

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.verify_user_email(mock_activation_token.token)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error during account activation" in exc_info.value.detail
    mock_db_session.rollback.assert_called_once()


# --- Tests for AuthService.login_user ---

@pytest.mark.asyncio
async def test_login_user_incorrect_credentials_user_not_found(auth_service, mock_db_session, user_login_data):
    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_first(None)  # No user found
    ]
    auth_service.mock_ph.verify_password.reset_mock()

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.login_user(user_login_data)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect username or password" in exc_info.value.detail
    mock_db_session.commit.assert_not_called()
    auth_service.mock_ph.verify_password.assert_not_called()


@pytest.mark.asyncio
async def test_login_user_inactive_account(auth_service, mock_db_session, user_login_data, mock_inactive_user):
    # CORRECTED: Only 1 execute call as it should raise HTTPException before delete/refresh
    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_first(mock_inactive_user),  # 1. User found
        # No more execute calls expected after inactive account leads to HTTPException
    ]
    auth_service.mock_ph.verify_password.return_value = True

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.login_user(user_login_data)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Account is not active. Please activate your account via email." in exc_info.value.detail
    mock_db_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_login_user_db_error_saving_refresh_token(auth_service, mock_db_session, user_login_data,
                                                        mock_active_user):
    auth_service.mock_ph.verify_password.return_value = True

    # CORRECTED: 3 execute calls
    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_first(mock_active_user),
        create_mock_execute_result_dml(),
        create_mock_execute_result_scalar_first(MagicMock(spec=RefreshToken))  # For db_session.refresh
    ]
    mock_db_session.add.side_effect = Exception("DB error on refresh token save")
    mock_db_session.refresh.side_effect = lambda obj: obj.id if isinstance(obj,
                                                                           MagicMock) else None  # Ensure refresh mock is good

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.login_user(user_login_data)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error saving refresh token" in exc_info.value.detail
    mock_db_session.rollback.assert_called_once()

# --- Tests for AuthService.refresh_tokens ---

@pytest.mark.asyncio
async def test_refresh_tokens_success(auth_service, mock_db_session, mock_refresh_token_db_obj, mock_active_user,
                                      mock_user_group):
    mock_refresh_token_db_obj.user = mock_active_user
    mock_active_user.group = mock_user_group

    # This mock's call is now correctly patched in the fixture
    auth_service.mock_decode_token.return_value = {"user_id": mock_active_user.id, "type": "refresh",
                                                   "sub": mock_active_user.username}

    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_first(mock_refresh_token_db_obj)
    ]
    # Add a mock for refresh in refresh_tokens as well, as it also calls refresh()
    mock_db_session.refresh.side_effect = lambda obj: obj.id if isinstance(obj, RefreshToken) else None

    token = await auth_service.refresh_tokens(mock_refresh_token_db_obj.token)

    auth_service.mock_decode_token.assert_called_once_with(mock_refresh_token_db_obj.token)
    auth_service.mock_create_access_token.assert_called_once()
    auth_service.mock_create_refresh_token.assert_not_called()

    mock_db_session.execute.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(mock_refresh_token_db_obj)

    assert isinstance(token, Token)
    assert token.access_token == "mock_access_token_value"
    assert token.refresh_token == mock_refresh_token_db_obj.token


@pytest.mark.asyncio
async def test_refresh_tokens_invalid_payload(auth_service, mock_db_session):
    # This mock is now correctly patched and its return value will be used
    auth_service.mock_decode_token.return_value = {"user_id": 1, "type": "access",
                                                   "sub": "someuser"}  # Non-refresh type payload

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.refresh_tokens("some_access_token")

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid refresh token payload" in exc_info.value.detail

    auth_service.mock_decode_token.assert_called_once()
    mock_db_session.execute.assert_not_called()


@pytest.mark.asyncio
async def test_refresh_tokens_not_found_or_expired(auth_service, mock_db_session, mock_active_user):
    auth_service.mock_decode_token.return_value = {"user_id": mock_active_user.id, "type": "refresh",
                                                   "sub": mock_active_user.username}
    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_first(None)  # No refresh token found in DB
    ]

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.refresh_tokens("non_existent_refresh_token")

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid or expired refresh token" in exc_info.value.detail
    mock_db_session.delete.assert_not_called()
    mock_db_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_refresh_tokens_expired_in_db(auth_service, mock_db_session, mock_expired_refresh_token_db_obj,
                                            mock_active_user):
    mock_expired_refresh_token_db_obj.user = mock_active_user

    auth_service.mock_decode_token.return_value = {"user_id": mock_active_user.id, "type": "refresh",
                                                   "sub": mock_active_user.username}
    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_first(mock_expired_refresh_token_db_obj)  # Expired token found in DB
    ]

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.refresh_tokens(mock_expired_refresh_token_db_obj.token)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid or expired refresh token" in exc_info.value.detail
    mock_db_session.delete.assert_called_once_with(mock_expired_refresh_token_db_obj)
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_refresh_tokens_user_not_found_or_inactive(auth_service, mock_db_session, mock_refresh_token_db_obj,
                                                         mock_inactive_user):
    auth_service.mock_decode_token.return_value = {"user_id": mock_inactive_user.id, "type": "refresh",
                                                   "sub": mock_inactive_user.username}
    mock_refresh_token_db_obj.user = mock_inactive_user

    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_first(mock_refresh_token_db_obj)
    ]

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.refresh_tokens(mock_refresh_token_db_obj.token)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "User not found or inactive" in exc_info.value.detail
    mock_db_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_refresh_tokens_db_error_updating_token(auth_service, mock_db_session, mock_refresh_token_db_obj,
                                                      mock_active_user):
    mock_refresh_token_db_obj.user = mock_active_user

    auth_service.mock_decode_token.return_value = {"user_id": mock_active_user.id, "type": "refresh",
                                                   "sub": mock_active_user.username}
    mock_db_session.execute.side_effect = [
        create_mock_execute_result_scalar_first(mock_refresh_token_db_obj)
    ]
    mock_db_session.commit.side_effect = Exception("DB update error during refresh token update")
    # Add a mock for refresh in refresh_tokens as well, as it also calls refresh()
    mock_db_session.refresh.side_effect = lambda obj: obj.id if isinstance(obj, RefreshToken) else None

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.refresh_tokens(mock_refresh_token_db_obj.token)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error updating refresh token" in exc_info.value.detail
    mock_db_session.rollback.assert_called_once()