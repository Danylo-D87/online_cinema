from sqlalchemy import Column, Integer, String

from src.database.setup import Base


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)

    def __repr__(self):
        return f"<Genre(name='{self.name}')>"
