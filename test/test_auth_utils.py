import pytest
from datetime import datetime, timedelta, UTC

from jose import jwt
from passlib.context import CryptContext
from passlib.exc import UnknownHashError

from src.core.security import PasswordHelper, create_access_token, create_refresh_token, decode_token
from src.config.settings import settings

from fastapi import HTTPException, status

from freezegun import freeze_time


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TestPasswordHelper:
    @staticmethod
    def test_get_password_hash():
        password = "testpassword"
        hashed_password = PasswordHelper.get_password_hash(password)
        assert isinstance(hashed_password, str)
        assert len(hashed_password) > 0
        assert PasswordHelper.verify_password(password, hashed_password)

    @staticmethod
    def test_verify_password_correct():
        password = "testpassword"
        hashed_password = PasswordHelper.get_password_hash(password)
        assert PasswordHelper.verify_password(password, hashed_password)

    @staticmethod
    def test_verify_password_incorrect():
        password = "testpassword"
        wrong_password = "wrongpassword"
        hashed_password = PasswordHelper.get_password_hash(password)
        assert not PasswordHelper.verify_password(wrong_password, hashed_password)

    @staticmethod
    def test_verify_password_invalid_hash():
        plain_password = "testpassword"
        invalid_hash = "invalid_hash_format"
        with pytest.raises(UnknownHashError):
            PasswordHelper.verify_password(plain_password, invalid_hash)


class TestTokenFunctions:

    @freeze_time("2025-01-01 12:00:00 UTC")
    def test_create_access_token(self):
        data = {"sub": "testuser"}
        token = create_access_token(data)

        decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert decoded_payload["sub"] == "testuser"

        expected_expiry = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        assert datetime.fromtimestamp(decoded_payload["exp"], tz=UTC) == expected_expiry


    @freeze_time("2025-01-01 12:00:00 UTC")
    def test_create_access_token_with_expires_delta(self):
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta)

        decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        expected_expiry = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC) + expires_delta
        assert datetime.fromtimestamp(decoded_payload["exp"], tz=UTC) == expected_expiry

    @freeze_time("2025-01-01 12:00:00 UTC")
    def test_create_refresh_token(self):
        data = {"sub": "testuser"}
        token = create_refresh_token(data)

        decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert decoded_payload["sub"] == "testuser"

        expected_expiry = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        assert datetime.fromtimestamp(decoded_payload["exp"], tz=UTC) == expected_expiry

    @freeze_time("2025-01-01 12:00:00 UTC")
    def test_create_refresh_token_with_expires_delta(self):
        data = {"sub": "testuser"}
        expires_delta = timedelta(days=30)
        token = create_refresh_token(data, expires_delta)

        decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        expected_expiry = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC) + expires_delta
        assert datetime.fromtimestamp(decoded_payload["exp"], tz=UTC) == expected_expiry

    @freeze_time("2025-01-01 12:00:00 UTC")
    def test_decode_token_valid(self):
        data = {"sub": "testuser", "exp": (datetime.now(UTC) + timedelta(minutes=5)).timestamp()}
        token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        decoded_payload = decode_token(token)
        assert decoded_payload["sub"] == "testuser"

    @freeze_time("2025-01-01 12:00:00 UTC")
    def test_decode_token_invalid_signature(self):
        data = {"sub": "testuser", "exp": (datetime.now(UTC) + timedelta(minutes=5)).timestamp()}
        invalid_secret_key = "wrong-secret-key"
        token = jwt.encode(data, invalid_secret_key, algorithm=settings.ALGORITHM)
        with pytest.raises(HTTPException) as excinfo:
            decode_token(token)
        assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in excinfo.value.detail

    @freeze_time("2025-01-01 12:00:00 UTC")
    def test_decode_token_expired(self):
        data = {"sub": "testuser", "exp": (datetime.now(UTC) - timedelta(minutes=5)).timestamp()}
        token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        with pytest.raises(HTTPException) as excinfo:
            decode_token(token)
        assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in excinfo.value.detail


    def test_decode_token_invalid_format(self):
        invalid_token = "this.is.not.a.valid.jwt"
        with pytest.raises(HTTPException) as excinfo:
            decode_token(invalid_token)
        assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in excinfo.value.detail

    @freeze_time("2025-01-01 12:00:00 UTC")
    def test_decode_token_missing_claims(self):
        data = {"some_other_claim": "value"}
        token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        decoded_payload = decode_token(token)
        assert "sub" not in decoded_payload
        assert "some_other_claim" in decoded_payload
        assert decoded_payload["some_other_claim"] == "value"
