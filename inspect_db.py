
from app.database.config import SessionLocal
from app.models.models import ReviewHistory, Category, AccessLog
from sqlalchemy import func

def inspect_database():
    db = SessionLocal()

    print("\n" + "="*60)
    print("DATABASE INSPECTION REPORT")
    print("="*60)

    print("\nCATEGORIES")
    print("-" * 60)
    categories = db.query(Category).all()
    for cat in categories:
        review_count = db.query(ReviewHistory).filter(
            ReviewHistory.category_id == cat.id
        ).count()

        latest_reviews_subquery = (
            db.query(
                ReviewHistory.review_id,
                func.max(ReviewHistory.created_at).label("max_created_at")
            )
            .filter(ReviewHistory.category_id == cat.id)
            .group_by(ReviewHistory.review_id)
            .subquery()
        )

        unique_review_count = db.query(latest_reviews_subquery).count()

        avg_stars = db.query(func.avg(ReviewHistory.stars)).filter(
            ReviewHistory.category_id == cat.id
        ).scalar()

        print(f"  {cat.id}. {cat.name}")
        print(f"     Description: {cat.description}")
        print(f"     Total history entries: {review_count}")
        print(f"     Unique reviews: {unique_review_count}")
        print(f"     Avg stars: {avg_stars:.2f}" if avg_stars is not None else "     Avg stars: 0")
        print()

    
    print("\nREVIEW STATISTICS")
    print("-" * 60)
    total_reviews = db.query(ReviewHistory).count()
    unique_reviews = db.query(ReviewHistory.review_id).distinct().count()

    print(f"  Total review history entries: {total_reviews}")
    print(f"  Unique reviews (by review_id): {unique_reviews}")
    print(f"  Reviews with edits: {total_reviews - unique_reviews}")

    
    missing_tone = db.query(ReviewHistory).filter(
        ReviewHistory.tone.is_(None)
    ).count()
    missing_sentiment = db.query(ReviewHistory).filter(
        ReviewHistory.sentiment.is_(None)
    ).count()

    print(f"\n  Reviews missing tone: {missing_tone}")
    print(f"  Reviews missing sentiment: {missing_sentiment}")

    
    print("\nRECENT REVIEWS (Latest 5)")
    print("-" * 60)
    recent = db.query(ReviewHistory).order_by(
        ReviewHistory.created_at.desc()
    ).limit(5).all()

    for review in recent:
        print(f"  ID: {review.id} | review_id: {review.review_id}")
        print(f"  Stars: {review.stars}/10")
        print(f"  Text: {review.text[:60]}..." if review.text and len(review.text) > 60 else f"  Text: {review.text}")
        print(f"  Tone: {review.tone} | Sentiment: {review.sentiment}")
        print(f"  Category: {review.category.name}")
        print(f"  Created: {review.created_at}")
        print()

    
    print("\n ACCESS LOGS (Latest 10)")
    print("-" * 60)
    logs = db.query(AccessLog).order_by(
        AccessLog.created_at.desc()
    ).limit(10).all()

    if logs:
        for log in logs:
            print(f"  [{log.created_at}] {log.text}")
    else:
        print("  No access logs yet. Make some API requests!")

    
    print("\nSTARS DISTRIBUTION")
    print("-" * 60)
    for stars in range(1, 11):
        count = db.query(ReviewHistory).filter(
            ReviewHistory.stars == stars
        ).count()
        bar = "█" * (count // 2) if count > 0 else ""
        print(f"  {stars:2d} stars: {bar} ({count})")

    
    print("\nSENTIMENT DISTRIBUTION")
    print("-" * 60)
    sentiments = db.query(
        ReviewHistory.sentiment,
        func.count(ReviewHistory.id)
    ).group_by(ReviewHistory.sentiment).all()

    for sentiment, count in sentiments:
        sentiment_display = sentiment if sentiment else "None (pending)"
        print(f"  {sentiment_display}: {count}")

    print("\n" + "="*60)
    print("End of report")
    print("="*60 + "\n")

    db.close()


if __name__ == "__main__":
    try:
        inspect_database()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure:")
        print("1. Docker services are running: docker-compose up -d")
        print("2. Database is migrated: alembic upgrade head")
