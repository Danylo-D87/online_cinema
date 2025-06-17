from datetime import datetime, UTC

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.database.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), nullable=False, unique=True, index=True)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime,
                        default=datetime.now(UTC), onupdate=datetime.now(UTC))

    group_id = Column(Integer, ForeignKey("user_groups.id"))
    group = relationship("UserGroup", back_populates="users")

    activation_tokens = relationship(
        "ActivationToken",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=True,
    )
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=True,
    )
    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    password_reset_token = relationship(
        "PasswordResetToken",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User(email='{self.email}', is_active={self.is_active})>"
