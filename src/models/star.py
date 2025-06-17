from sqlalchemy import Column, Integer, String
from src.database.base import Base


class Star(Base):
    __tablename__ = "stars"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    def __repr__(self):
        return f"<Star(name='{self.name}')>"
