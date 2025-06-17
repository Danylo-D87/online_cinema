import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from src.database.base import Base


class GenderEnum(enum.Enum):
    MAN = "man"
    WOMAN = "woman"


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    avatar = Column(String, nullable=True)
    gender = Column(enum.Enum(GenderEnum), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    info = Column(Text, nullable=True)

    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id}, first_name='{self.first_name}')>"
