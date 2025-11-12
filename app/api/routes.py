from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from app.database.config import get_db
from app.models.models import ReviewHistory, Category
from app.schemas.schemas import CategoryTrend, ReviewListResponse, ReviewResponse
from app.tasks.tasks import log_access, analyze_sentiment_and_tone

router = APIRouter()


@router.get("/reviews/trends", response_model=List[CategoryTrend])
async def get_review_trends(db: Session = Depends(get_db)):
    log_access.delay("GET /reviews/trends")

    latest_reviews_subquery = (
        db.query(
            ReviewHistory.review_id,
            func.max(ReviewHistory.created_at).label("max_created_at")
        )
        .group_by(ReviewHistory.review_id)
        .subquery()
    )

    latest_reviews = (
        db.query(ReviewHistory)
        .join(
            latest_reviews_subquery,
            (ReviewHistory.review_id == latest_reviews_subquery.c.review_id) &
            (ReviewHistory.created_at == latest_reviews_subquery.c.max_created_at)
        )
        .subquery()
    )

    results = (
        db.query(
            Category.id,
            Category.name,
            Category.description,
            func.avg(latest_reviews.c.stars).label("average_stars"),
            func.count(latest_reviews.c.id).label("total_reviews")
        )
        .join(latest_reviews, Category.id == latest_reviews.c.category_id)
        .group_by(Category.id, Category.name, Category.description)
        .order_by(desc("average_stars"))
        .limit(5)
        .all()
    )

    return [
        CategoryTrend(
            id=row.id,
            name=row.name,
            description=row.description,
            average_stars=float(row.average_stars),
            total_reviews=row.total_reviews
        )
        for row in results
    ]


@router.get("/reviews/", response_model=ReviewListResponse)
async def get_reviews_by_category(
    category_id: int = Query(..., description="Category ID to filter reviews"),
    cursor: Optional[int] = Query(None, description="Cursor for pagination (review history id)"),
    db: Session = Depends(get_db)
):
    log_access.delay(f"GET /reviews/?category_id={category_id}")

    page_size = 15

    latest_reviews_subquery = (
        db.query(
            ReviewHistory.review_id,
            func.max(ReviewHistory.created_at).label("max_created_at")
        )
        .filter(ReviewHistory.category_id == category_id)
        .group_by(ReviewHistory.review_id)
        .subquery()
    )

    query = (
        db.query(ReviewHistory)
        .join(
            latest_reviews_subquery,
            (ReviewHistory.review_id == latest_reviews_subquery.c.review_id) &
            (ReviewHistory.created_at == latest_reviews_subquery.c.max_created_at)
        )
        .filter(ReviewHistory.category_id == category_id)
    )

    if cursor:
        query = query.filter(ReviewHistory.id < cursor)

    reviews = (
        query
        .order_by(desc(ReviewHistory.created_at))
        .limit(page_size + 1)  
        .all()
    )

    has_more = len(reviews) > page_size
    if has_more:
        reviews = reviews[:page_size]

    next_cursor = reviews[-1].id if has_more and reviews else None

    review_responses = []
    for review in reviews:
        if (review.tone is None or review.sentiment is None) and review.text:
            analyze_sentiment_and_tone.delay(review.id, review.text, review.stars)

        review_responses.append(ReviewResponse.model_validate(review))

    return ReviewListResponse(
        reviews=review_responses,
        next_cursor=next_cursor,
        has_more=has_more
    )
