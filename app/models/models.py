from sqlalchemy import Column, BigInteger, String, Integer, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.config import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    review_histories = relationship("ReviewHistory", back_populates="category")


class ReviewHistory(Base):
    __tablename__ = "review_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    text = Column(String, nullable=True)
    stars = Column(Integer, nullable=False)
    review_id = Column(String(255), nullable=False, index=True)
    tone = Column(String(255), nullable=True)
    sentiment = Column(String(255), nullable=True)
    category_id = Column(BigInteger, ForeignKey("categories.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint('stars >= 1 AND stars <= 10', name='check_stars_range'),
    )

    category = relationship("Category", back_populates="review_histories")


class AccessLog(Base):
    __tablename__ = "access_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    text = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
