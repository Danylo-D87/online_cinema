from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, UTC

from src.database.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    group_id = Column(Integer, ForeignKey("user_groups.id"), default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC), nullable=False)

    group = relationship("UserGroup", backref="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    favorite_movies = relationship("FavoriteMovie", back_populates="user")
    activation_tokens = relationship("ActivationToken", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
