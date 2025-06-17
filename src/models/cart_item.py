from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from src.database.base import Base


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint('cart_id', 'movie_id', name='_cart_movie_uc'),
    )

    cart = relationship("Cart", back_populates="items")
    movie = relationship("Movie")

    def __repr__(self):
        return f"<CartItem(cart_id={self.cart_id}, movie_id={self.movie_id})>"
