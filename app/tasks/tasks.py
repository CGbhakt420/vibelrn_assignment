from app.celery_app import celery_app
from app.database.config import SessionLocal
from app.models.models import AccessLog, ReviewHistory
from app.database.config import settings
import anthropic


@celery_app.task
def log_access(endpoint: str):
    db = SessionLocal()
    try:
        access_log = AccessLog(text=endpoint)
        db.add(access_log)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


@celery_app.task
def analyze_sentiment_and_tone(review_history_id: int, text: str, stars: int):
    db = SessionLocal()
    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

        prompt = f"""Analyze the following review and provide both the tone and sentiment.

Review Text: "{text}"
Star Rating: {stars}/10

Please respond in the following exact format:
Tone: [one word describing the tone, e.g., Professional, Casual, Enthusiastic, Disappointed, Angry, Happy, Neutral]
Sentiment: [one word: Positive, Negative, or Neutral]

Keep your response concise with just these two lines."""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = message.content[0].text

        tone = None
        sentiment = None

        for line in response_text.strip().split('\n'):
            if line.startswith('Tone:'):
                tone = line.split(':', 1)[1].strip()
            elif line.startswith('Sentiment:'):
                sentiment = line.split(':', 1)[1].strip()

        review = db.query(ReviewHistory).filter(ReviewHistory.id == review_history_id).first()
        if review:
            review.tone = tone
            review.sentiment = sentiment
            db.commit()

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
