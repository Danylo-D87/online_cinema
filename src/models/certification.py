from sqlalchemy import Column, Integer, String
from src.database.base import Base
from sqlalchemy.orm import relationship


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    movies = relationship("Movie", back_populates="certification")

    def __repr__(self):
        return f"<Certification(name='{self.name}')>"
