from app.database.config import SessionLocal
from app.models.models import Category, ReviewHistory
from datetime import datetime, timedelta
import random

def seed_database():
    db = SessionLocal()

    try:
        categories_data = [
            {"name": "Electronics", "description": "Electronic products and gadgets"},
            {"name": "Books", "description": "Books and literature"},
            {"name": "Clothing", "description": "Apparel and fashion"},
            {"name": "Home & Kitchen", "description": "Home and kitchen items"},
            {"name": "Sports", "description": "Sports and outdoor equipment"},
            {"name": "Toys", "description": "Toys and games"},
        ]

        existing_categories = {c.name for c in db.query(Category).all()}

        new_categories = []
        for cat in categories_data:
            if cat["name"] not in existing_categories:
                new_categories.append(Category(**cat))

        if new_categories:
            db.add_all(new_categories)
            db.commit()
            print(f"Created {len(new_categories)} new categories")
        else:
            print("All categories already exist, skipping category creation")


        categories = db.query(Category).all()

        positive_reviews = [
            "Excellent product! Highly recommend.",
            "Great quality and fast shipping.",
            "Love it! Exactly what I needed.",
            "Outstanding! Will buy again.",
            "Perfect! Exceeded my expectations.",
        ]

        neutral_reviews = [
            "It's okay, does the job.",
            "Average product, nothing special.",
            "Decent for the price.",
            "Works as described.",
            "Fine, but could be better.",
        ]

        negative_reviews = [
            "Disappointed with the quality.",
            "Not what I expected.",
            "Poor quality, would not recommend.",
            "Broke after a week of use.",
            "Waste of money.",
        ]

        existing_review_ids = {
            r.review_id for r in db.query(ReviewHistory.review_id).distinct()
        }

        review_count = 0
        for category in categories:
            num_reviews = random.randint(10, 20)

            for i in range(num_reviews):
                review_id = f"review_{category.name.lower().replace(' ', '_')}_{i+1}"
                if review_id in existing_review_ids:
                    continue  

                review_type = random.choice(['positive', 'neutral', 'negative'])
                if review_type == 'positive':
                    text = random.choice(positive_reviews)
                    stars = random.randint(8, 10)
                    tone = random.choice(["Enthusiastic", "Happy", "Satisfied"])
                    sentiment = "Positive"
                elif review_type == 'neutral':
                    text = random.choice(neutral_reviews)
                    stars = random.randint(5, 7)
                    tone = random.choice(["Neutral", "Professional", "Casual"])
                    sentiment = "Neutral"
                else:
                    text = random.choice(negative_reviews)
                    stars = random.randint(1, 4)
                    tone = random.choice(["Disappointed", "Angry", "Frustrated"])
                    sentiment = "Negative"

                created_time = datetime.now() - timedelta(days=random.randint(1, 90))

                review = ReviewHistory(
                    text=text,
                    stars=stars,
                    review_id=review_id,
                    category_id=category.id,
                    tone=tone,
                    sentiment=sentiment,
                    created_at=created_time,
                    updated_at=created_time
                )

                db.add(review)
                review_count += 1

                if random.random() < 0.2:
                    num_edits = random.randint(1, 3)
                    for j in range(num_edits):
                        edit_time = created_time + timedelta(days=random.randint(1, 10))
                        edited_id = f"{review_id}_edit{j+1}"

                        if edited_id in existing_review_ids:
                            continue

                        edited_review = ReviewHistory(
                            text=text + " (Edited)",
                            stars=min(10, stars + random.randint(-1, 1)),
                            review_id=edited_id,
                            category_id=category.id,
                            tone=tone,
                            sentiment=sentiment,
                            created_at=edit_time,
                            updated_at=edit_time
                        )

                        db.add(edited_review)
                        review_count += 1

        db.commit()
        print(f"Created {review_count} new review history entries")

        for i in range(5):
            review_id = f"review_no_analysis_{i+1}"
            if review_id in existing_review_ids:
                continue

            review = ReviewHistory(
                text="This product needs AI analysis for tone and sentiment.",
                stars=random.randint(1, 10),
                review_id=review_id,
                category_id=random.choice(categories).id,
                tone=None,
                sentiment=None,
            )
            db.add(review)

        db.commit()
        print("Ensured LLM test reviews exist")

        print("\nDatabase seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Seeding database with sample data...")
    seed_database()
