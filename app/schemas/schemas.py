from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CategoryTrend(BaseModel):
    id: int
    name: str
    description: Optional[str]
    average_stars: float
    total_reviews: int

    class Config:
        from_attributes = True


class ReviewResponse(BaseModel):
    id: int
    text: Optional[str]
    stars: int
    review_id: str
    created_at: datetime
    tone: Optional[str]
    sentiment: Optional[str]
    category_id: int

    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    reviews: List[ReviewResponse]
    next_cursor: Optional[int]
    has_more: bool
