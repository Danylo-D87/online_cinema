import enum
from src.database.base import Base
from sqlalchemy import Column, Integer, String


class UserGroupEnum(enum.Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class UserGroup(Base):
    __tablename__ = "user_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)

    def __repr__(self):
        return f"<UserGroup {self.name}>"

